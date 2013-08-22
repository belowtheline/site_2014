require 'fileutils'
require 'find'
require 'json'
require 'pathname'

require 'bundler/setup'
Bundler.require(:development)

OUTPUT_DIR = 'site'
TEMPLATE_DIR = 'templates'

task :output_dirs do
  %w{division state news js css}.each do |dirname|
    FileUtils.mkdir_p(File.join(OUTPUT_DIR, dirname))
  end
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
    scaf_locals[:body] = '<div class="row"><div class="col-lg-8">' + body +
    '</div></div>'
  end

  if not scaf_locals.has_key? :title then
    scaf_locals[:title] = nil
  end
  if not scaf_locals.has_key? :base then
    scaf_locals[:base] = nil
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

  content[0] = '<div class="page-header">' + content[0] + '</div>'

  if done_teaser
    puts "HERE"
    target_link = "<a href=\"#{target_filename}\">Read more...</a>"
    teaser_content.push("<p><strong>#{target_link}</strong></p>")

    teaser_content[0].sub! /<h1 id=".*?">/, '<p class="lead"><strong>'
    teaser_content[0].sub! /<\/h1>/, '</strong></p>'
  end

  return content.join(''), teaser_content.join('')
end

task default: :site

desc "Build site"
task site: [:output_dirs, :images, :js, :css, :content, :sitemap, :pdfballots]

desc "Build content from templates & data"
task content: [:output_dirs] do
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

  postfiles = Dir.glob('content/news/*.md').sort.map { |s| s.split('/')[-1] }
  postfiles.each do |filename|
    match = filename.match /^(.*)_(.*)\.md$/
    timestamp = DateTime.iso8601(match[1])
    poster = Posters[match[2]]
    target = timestamp.strftime(PostFilenameFormat)

    attribution = "Posted by #{poster} at #{timestamp.strftime(PostDateFormat)}"
    attribution = '<div class="post-attribution">' + attribution + '</div>'

    body, teaser = load_content(File.join('news', filename), target)
    body = '<div>' + body + '</div>'

    puts body
    title = body.match(/<h1.*?>(.*?)<\/h1>/)[1]

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
  output('about-us.html', load_content('about-us.md', nil)[0], {}, {title: "About Us"})
  output('privacy.html', load_content('privacy.md', nil)[0], {}, {title: "Privacy Policy"})
  output('news.html', template('news'), { posts: posts },
    {title: "News"})

  File.write(File.join(OUTPUT_DIR, 'parties.json'), JSON.generate(parties))
  output('ballotpicker.html', template('ballotpicker'), {}, {title: 'Ballot Editor', base: '/editor/'})
  output('ticketviewer.html', template('ticketviewer'), {}, {title: 'Ticket Viewer', base: '/viewer/'})

  Parallel.each(divisions.keys) do |division_id|
    division = divisions[division_id]
    candidates = candidates_reps["division/#{division_id}"] || []
    candidates.sort! { |a, b| a['ballot_position'] <=> b['ballot_position'] }

    division_data = {
      division: division,
      division_id: division_id,
      states: states,
      representative: representatives["division/#{division_id}"],
      candidates: candidates,
    }
    output(
      File.join('division', "#{division_id}.html"),
      template('division'),
      division_data.merge(partytmpl: partytmpl, parties: parties, senators: senators[division['state']]),
      {title: division['name']}
    )
    File.write(File.join(OUTPUT_DIR, 'division', "#{division_id}.json"), JSON.generate(division_data))

  end

  states.each do |state_id, state|
    candidates = {}
    ballot_order = []

    people.each do |person_id, person|
      next if person['candidate'] != "state/#{state_id}"
      candidates[person_id] = person
      ballot_order.push [person_id, person['group'], person['ballot_position']]
    end

    ballot_order.sort! do |a, b|
      if a[1] == b[1]
        a[2] <=> b[2]
      elsif a[1].length != b[1].length
        a[1].length <=> b[1].length
      else
        a[1] <=> b[1]
      end
    end
    ballot_order.map! { |a| a[0] }

    if state_id.match /t$/ then
      state_or_territory = 'territory'
    else
      state_or_territory = 'state'
    end

    groups = {}

    Dir.foreach("data/groups") do |name|
      next unless name =~ /^#{state_id}-[A-Z]+\.json$/
      data = JSON.parse(File.read(File.join('data', 'groups', name)))
      name.sub!(/^#{state_id}-([A-Z]+)\.json$/, '\1')
      groups[name] = data
    end

    state_data = {
      state: state,
      state_id: state_id,
      state_or_territory: state_or_territory,
      senators: senators["state/#{state_id}"],
      candidates: candidates,
      ballot_order: ballot_order,
      groups: groups,
    }

    output(
      File.join('state', "#{state_id}.html"),
      template('state'),
      state_data.merge(partytmpl: partytmpl, parties: parties),
      {title: state['name']}
    )

    File.write(File.join(OUTPUT_DIR, 'state', "#{state_id}.json"), JSON.generate(state_data))
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
  FileUtils.cp_r('images', File.join(OUTPUT_DIR))
  FileUtils.mv(File.join(OUTPUT_DIR, 'images', 'favicon.ico'), File.join(OUTPUT_DIR, 'favicon.ico'))
end

desc "Build & Copy JS into site directory (requires uglify-js)"
task js: [:output_dirs] do
  FileUtils.cp(Dir.glob('vendor/*.js'), File.join(OUTPUT_DIR, 'js'))
  FileUtils.cp(Dir.glob('js/*.js'), File.join(OUTPUT_DIR, 'js'))
end

desc "Build & Copy CSS into site directory (requires lessc)"
task css: [:output_dirs] do
  res = system "lessc vendor/bootstrap/less/bootstrap.less site/css/bootstrap.css"
  if not res then
    puts "lessc failed, is it installed?"
  end
  system "lessc less/app.less site/css/app.css"
end

desc "Generate ballot data for PDF renderer"
task :pdfballots do
  res = system "python pdfprep.py"
  if not res
    puts "pdfprep.py failed"
  end
  FileUtils.mv("ballots.pck", "api/ballots.pck")
end

desc "Serve site on port 8000"
task :serve do
  require 'webrick'

  server = WEBrick::HTTPServer.new Port: 8000, DocumentRoot: OUTPUT_DIR
  server.mount_proc '/editor' do |req, res|
    res.body = File.read(File.join(OUTPUT_DIR, 'ballotpicker.html'))
  end
  server.mount_proc '/viewer' do |req, res|
    res.body = File.read(File.join(OUTPUT_DIR, 'ticketviewer.html'))
  end
  trap 'INT' do server.shutdown end
  puts "Serving on http://127.0.0.1:8000"
  server.start
end

desc "Build Sitemap"
task :sitemap do
  sitemap = File.open(File.join(OUTPUT_DIR, 'sitemap.xml.gz'), 'w')
  sitemap = Zlib::GzipWriter.new(sitemap)

  xml = Builder::XmlMarkup.new(target: sitemap, indent: 2)
  xml.instruct! :xml, encoding: "UTF-8"
  xml.urlset(xmlns: 'http://www.sitemaps.org/schemas/sitemap/0.9') do |urlset|
    Find.find(OUTPUT_DIR) do |filename|
      next if not filename.match /\.html$/

      xml.url do |url|
        url.loc 'http://belowtheline.org.au/' + filename.sub(/^site\//, '')
        url.lastmod File.stat(filename).mtime.strftime('%Y-%m-%d')
        url.changefreq 'hourly'
      end
    end
  end

  sitemap.close
end

