require 'fileutils'
require 'find'
require 'json'
require 'pathname'

require 'bundler/setup'
Bundler.require(:development)

OUTPUT_DIR = 'site'
TEMPLATE_DIR = 'templates'

task :output_dirs do
  FileUtils.mkdir_p(OUTPUT_DIR)
  FileUtils.mkdir_p(File.join(OUTPUT_DIR, 'division'))
  FileUtils.mkdir_p(File.join(OUTPUT_DIR, 'state'))
  FileUtils.mkdir_p(File.join(OUTPUT_DIR, 'news'))
end

def template(name)
  return Haml::Engine.new(File.read(File.join(TEMPLATE_DIR, "#{name}.haml")))
end

def layout
  @layout ||= template('layout')
end

def output(name, body, locals={}, scaf_locals={})
  puts "Outputting #{name}..."

  if body.kind_of? Haml::Engine then
    scaf_locals[:body] = body.render(Object.new, locals)
  else
    scaf_locals[:body] = '<div class="row"><div class="span12">' + body +
    '</div></div>'
  end

  if not scaf_locals.has_key? :title then
    scaf_locals[:title] = nil
  end

  content = layout.render(Object.new, scaf_locals)
  File.write(File.join(OUTPUT_DIR, name), content)
end

def load(category)
  hash = {}

  Dir.foreach("data/#{category}") do |name|
    next unless name =~ /\.json$/
    data = JSON.parse(File.read(File.join('data', category, name)))
    name.sub!(/\.json$/, '')
    hash[name] = data
  end

  return hash
end

Posters = {
  'benno' => "Benno Rice"
}

PostDateFormat = "%I:%M%P EST on %B %-d, %Y"
PostFilenameFormat = "news/%Y-%m-%dT%H:%M.html"

def load_content(filename, target_filename)
  filename = File.join('content', filename)

  content = []
  teaser_content = []
  done_teaser = false
  Kramdown::Document.new(File.read(filename)).to_html.lines.each do |line|
    if line.match /-- BREAK --/ then
      done_teaser = true
      next
    end

    content.push(line)
    if not done_teaser then
      teaser_content.push(line)
    end
  end

  target_link = "<a href=\"#{target_filename}\">Read more...</a>"
  teaser_content.push("<p><strong>#{target_link}</strong></p>")

  content[0] = '<div class="page-header">' + content[0] + '</div>'
  teaser_content[0].sub! /<h1 id=".*?">/, '<p class="lead"><strong>'
  teaser_content[0].sub! /<\/h1>/, '</strong></p>'

  return content.join(''), teaser_content.join('')
end

task default: :site

desc "Generate templates & build site"
task site: [:output_dirs, :images, :js, :css] do
  partytmpl = template('party')

  states = load('state')
  divisions = load('division')
  people = load('people')
  parties = load('parties')

  representatives = {}
  senators = {}

  candidates_reps = {}
  candidates_senate = {}

  state_list = states.keys.sort

  people.each do |person_id, person|
    if person.has_key? 'party' and not parties.has_key? person['party'] then
      raise "Party not known: #{person['party']}"
    end

    if person.has_key? 'candidate' then
      if person['candidate'].match /^state/ then
        candidates = candidates_senate
      else
        candidates = candidates_reps
      end

      candidates[person['candidate']] ||= []
      candidates[person['candidate']].push(person)
    end

    next if not person.has_key? 'elected'

    if person['elected'].match /^state/ then
      senators[person['elected']] ||= []
      senators[person['elected']].push(person)
    else
      representatives[person['elected']] = person
    end

    if person.has_key? 'party' then
      if not parties.has_key? person['party'] then
        puts "Missing party: #{person['party']}"
      end
    end
  end

  teaser = nil
  posts = {}

  Dir.foreach("content/news") do |filename|
    next if not filename.match /\.md$/

    match = filename.match /^(.*)_(.*)\.md$/
    timestamp = DateTime.iso8601(match[1])
    poster = Posters[match[2]]
    target = timestamp.strftime(PostFilenameFormat)

    attribution = "Posted by #{poster} at #{timestamp.strftime(PostDateFormat)}"
    attribution = '<div class="post-attribution">' + attribution + '</div>'

    body, teaser = load_content(File.join('news', filename), target)
    body = '<div>' + body + '</div>'

    title = body.match(/<strong>(.*?)<\/strong>/)[1]

    posts[timestamp.to_date] ||= []
    posts[timestamp.to_date].push([title, target])

    output(target, body, {}, {title: title})
  end

  intro, index_intro = load_content('intro.md', 'intro.html')

  output('index.html', template('index'), {
    states: states,
    state_list: state_list,
    divisions: divisions,
    intro: index_intro,
    news: teaser,
    })

  output('intro.html', intro, {}, {title: "Introduction"})
  output('news.html', template('news'), { posts: posts },
    {title: "News"})

  divisions.each do |division_id, division|
    if division['state'].match /t$/ then
      state_or_territory = 'territory'
    else
      state_or_territory = 'state'
    end

    output(File.join('division', "#{division_id}.html"),
     template('division'), {
      division: division,
      representative: representatives["division/#{division_id}"],
      senators: senators[division['state']],
      state_or_territory: state_or_territory,
      parties: parties,
      candidates: candidates_reps["division/#{division_id}"] || [],
      partytmpl: partytmpl,
      }, {title: division['name']})
  end

  states.each do |state_id, state|
    candidates = candidates_senate["state/#{state_id}"] || []
    candidates.sort! do |a, b|
      if a['party'] == b['party'] then
        a['ballot_position'] <=> b['ballot_position']
      elsif a.has_key? 'party' and b.has_key? 'party' then
        parties[a['party']]['name'] <=> parties[b['party']]['name']
      elsif a.has_key? 'party' then
        1
      elsif b.has_key? 'party' then
        -1
      else
        0
      end
    end

    if state_id.match /t$/ then
      state_or_territory = 'territory'
    else
      state_or_territory = 'state'
    end

    output(File.join('state', "#{state_id}.html"),
     template('state'), {
      state: state,
      state_or_territory: state_or_territory,
      senators: senators["state/#{state_id}"],
      parties: parties,
      candidates: candidates || [],
      partytmpl: partytmpl,
      }, {title: state['name']})
  end

end

desc "Upload site to Rackspace"
task upload: [:site] do
  storage = Fog::Storage.new(provider: 'Rackspace', rackspace_region: :syd)
  directory = storage.directories.get "live"
  if directory == nil
    directory = storage.directories.create key: "live"
  end

  Find.find(OUTPUT_DIR) do |f|
    next if File.directory?(f)

    path = Pathname.new(f).relative_path_from(Pathname.new(OUTPUT_DIR)).to_s
    puts "Uploading #{path}..."
    file = directory.files.create key: path, body: File.open(f)
  end

  directory.metadata["Web-Index"] = 'index.html'
  directory.save
end

desc "Copy images into site directory"
task images: [:output_dirs] do
  FileUtils.cp_r('images', File.join(OUTPUT_DIR, 'images'))
end

desc "Build & Copy JS into site directory (requires uglify-js)"
task js: [:output_dirs] do
  system "uglifyjs vendor/bootstrap/js/*.js -c > site/js/bootstrap.js"
  FileUtils.cp(Dir.glob('vendor/*.js'), File.join(OUTPUT_DIR, 'js'))
  FileUtils.cp(Dir.glob('js/*.js'), File.join(OUTPUT_DIR, 'js'))
end

desc "Build & Copy CSS into site directory (requires lessc)"
task css: [:output_dirs] do
  system "lessc vendor/bootstrap/less/bootstrap.less site/css/bootstrap.css"
end

desc "Serve site on port 8000 (requires Python)"
task :serve do
  system "cd site; python -m SimpleHTTPServer &"
end

