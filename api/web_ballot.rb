require 'json'

require "rubygems"
require "sinatra/base"

require 'bundler/setup'
Bundler.require(:development)

SHORTREV = `git rev-parse --short HEAD`.strip() || 'xxx'

TemplateDir = File.join('..', 'templates')
Layout = Haml::Engine.new(File.read(File.join(TemplateDir, 'layout.haml')))
Ballot = Haml::Engine.new(File.read(File.join(TemplateDir, 'ballot.haml')))

SiteDir = File.join('..', 'site')

Divisions = {}

Dir.glob(File.join(SiteDir, 'division', '*.json')).each do |division_file|
  division = JSON.parse(File.read(division_file))
  Divisions[division['division_id']] = division
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
    state = division['division']['state'].split('/')[1]
    state = division['states'][state]
    division_candidates = Array.new(division['candidates'])
    division_ticket = ticket['division_ticket'].split(',')
    division_candidates.zip(division_ticket).each do |candidate, preference|
      candidate['preference'] = preference
    end

    locals[:body] = Ballot.render(Object.new, {
      division_name: division['division']['name'],
      state_name: state['name'],
      division_candidates: division_candidates,
      parties: Parties,
    })

    return Layout.render(Object.new, locals)
  end

end
