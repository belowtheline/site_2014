require 'json'

require "rubygems"
require "sinatra/base"

require 'bundler/setup'
Bundler.require

def path(p)
  File.expand_path File.join('..', p), __FILE__
end

BALLOT_STORE = path(File.join('..', 'site', 'ballots'))
SHORTREV = `git rev-parse --short HEAD`.strip() || 'xxx'

if not Dir.exists? BALLOT_STORE
  Dir.mkdir(BALLOT_STORE)
end

TemplateDir = path(File.join('..', 'templates'))
Layout = Haml::Engine.new(File.read(File.join(TemplateDir, 'layout.haml')))
Ballot = Haml::Engine.new(File.read(File.join(TemplateDir, 'ballot.haml')))

SiteDir = path(File.join('..', 'site'))

Divisions = {}
States = {}

Dir.glob(File.join(SiteDir, 'division', '*.json')).each do |division_file|
  division = JSON.parse(File.read(division_file))
  Divisions[division['division_id']] = division
end

Dir.glob(File.join(SiteDir, 'state', '*.json')).each do |state_file|
  state = JSON.parse(File.read(state_file))
  group_order = state['candidates'].values.map {|c| c['group']}
  group_order.uniq!
  group_order.reject! {|g| g == 'UG'}
  group_order.sort! do |a, b|
    if a.length != b.length
      a.length <=> b.length
    else
      a <=> b
    end
  end
  state['group_order'] = group_order
  state['ungrouped'] = state['ballot_order'].reject do |candidate_id|
    candidate = state['candidates'][candidate_id]
    candidate['group'] != 'UG'
  end

  state['groups'].each do |group_id, group|
    group['candidates'].sort! do |a, b|
      state['ballot_order'].index(a) <=> state['ballot_order'].index(b)
    end
  end

  States[state['state_id']] = state
end

Parties = JSON.parse(File.read(File.join(SiteDir, 'parties.json')))

class WebBallot < Sinatra::Base

  set :public_folder, SiteDir

  get '/ballot/:ballot_id' do
    locals = {
      base: nil,
      title: 'Ballot',
      shortrev: SHORTREV,
      rollbar_environment: ENV['BTL_PRODUCTION'] ? 'production' : 'debug',
    }

    redis = Redis.new(:db => 5)
    ticket = redis.hgetall(params[:ballot_id])

    division = Divisions[ticket['division']]
    state_id = division['division']['state'].split('/')[1]
    state = division['states'][state_id]
    division_candidates = Array.new(division['candidates'])
    division_ticket = ticket['division_ticket'].split(',')
    division_candidates.zip(division_ticket).each do |candidate, preference|
      candidate['preference'] = preference
    end

    if ticket['order_by_group'].to_i
      group_order = States[state_id]['group_order']
      ungrouped = (1..States[state_id]['ungrouped'].length).to_a
      ungrouped.map! {|a| "UG#{a}"}
      group_order += ungrouped
      group_ticket = ticket['senate_ticket'].split(',')
      group_ticket = group_ticket.map {|a| a.to_i}.zip(group_order)
      group_ticket.sort! {|a, b| a[0] <=> b[0]}
      counter = 1
      state_ticket = group_ticket.map do |a|
        a = a[1]
        if a.slice(0, 2) == 'UG'
          b = a.slice(2).to_i - 1
          counter += 1
          [a, [counter]]
        else
          candidates = States[state_id]['groups'][a]['candidates']
          start = counter
          counter += candidates.length
          [a, (start..(counter - 1)).to_a]
        end
      end
      state_ticket.sort! do |a, b|
        if a[0].length != b[0].length
          a[0].length <=> b[0].length
        else
          a[0] <=> b[0]
        end
      end
      state_ticket.map! {|a| a[1]}
      state_ticket.flatten!
    else
      state_ticket = ticket['senate_ticket'].split(',')
    end

    locals[:body] = Ballot.render(Object.new, {
      division_name: division['division']['name'],
      state_name: state['name'],
      division_candidates: division_candidates,
      parties: Parties,
      state: States[state_id],
      state_ticket: state_ticket,
    })

    content = Layout.render(Object.new, locals)
    File.write(File.join(BALLOT_STORE, "#{params[:ballot_id]}.html"), content)
    return content
  end

end
