require 'fileutils'
require 'find'
require 'json'
require 'pathname'

require 'fog'
require 'haml'
require 'kramdown'

OUTPUT_DIR = 'site'
TEMPLATE_DIR = 'templates'
DATA_DIR = File.join(OUTPUT_DIR, 'data')

task :output_dirs do
    FileUtils.mkdir_p(OUTPUT_DIR)
    FileUtils.mkdir_p(DATA_DIR)
    FileUtils.mkdir_p(File.join(OUTPUT_DIR, 'division'))
    FileUtils.mkdir_p(File.join(DATA_DIR, 'senators'))
    FileUtils.mkdir_p(File.join(OUTPUT_DIR, 'news'))
end

task :data => [:output_dirs] do
    blob = {:state => {}, :division => {}, :representatives => {},
            :senators => {}}
    representatives = {}
    senators = {}
    people = {}

    Dir.foreach('data/people') do |name|
        next unless name =~ /\.json$/
        data = JSON.parse(File.read(File.join('data', 'people', name)))

        if data['elected'].match /^division/ then
            representatives[data['elected']] = data
        else
            state = data['elected']
            if not senators.key? state then
                senators[state] = []
            end
            name.sub!(/\.json$/, '')
            senators[state].push name
            people[name] = data
        end
    end

    File.write(File.join(DATA_DIR, 'senators.json'), JSON.generate(senators));

    Dir.foreach('data/state') do |name|
        next unless name =~ /\.json$/
        data = JSON.parse(File.read(File.join('data', 'state', name)))
        name.sub!(/\.json$/, '')
        blob[:state][name] = data

        File.write(File.join(DATA_DIR, "senators/#{name}.json"),
            JSON.generate(senators["state/#{name}"].map { |n| people[n] }))
    end

    Dir.foreach('data/division') do |name|
        next unless name =~ /\.json$/
        data = JSON.parse(File.read(File.join('data', 'division', name)))
        name.sub!(/\.json$/, '')
        blob[:division][name] = data

        File.write(File.join(DATA_DIR, "#{name}.json"),
            JSON.generate(representatives["division/#{name}"]));
    end

    File.write(File.join(DATA_DIR, 'data.js'),
        "var _btldata = " + JSON.generate(blob) + ";")
end

def template(name)
    return Haml::Engine.new(File.read(File.join(TEMPLATE_DIR, "#{name}.haml")))
end

Scaffold = template('scaffold')

def output(name, body, locals={}, scaf_locals={})
    if body.kind_of? Haml::Engine then
        scaf_locals[:body] = body.render(Object.new, locals)
    else
        scaf_locals[:body] = '<div class="row"><div class="span12">' + body +
            '</div></div>'
    end

    if not scaf_locals.has_key? :title then
        scaf_locals[:title] = nil
    end

    content = Scaffold.render(Object.new, scaf_locals)
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

task :site => [:output_dirs] do
    states = load('state')
    divisions = load('division')
    people = load('people')
    parties = load('parties')

    representatives = {}
    senators = {}

    candidates_reps = {}
    candidates_senate = {}

    people.each do |person_id, person|
        if person.has_key? 'candidate' then
            if person['candidate'].match /^state/ then
                candidates = candidates_senate
            else
                candidates = candidates_reps
            end

            if not candidates.has_key? person['candidate'] then
                candidates[person['candidate']] = []
            end
            candidates[person['candidate']].push(person)
        end

        next if not person.has_key? 'elected'

        if person['elected'].match /^state/ then
            if not senators.has_key? person['elected'] then
                senators[person['elected']] = []
            end
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

        if not posts.has_key? timestamp.to_date then
            posts[timestamp.to_date] = []
        end
        posts[timestamp.to_date].push([title, target])

        output(target, body, {}, {:title => title})
    end

    intro, index_intro = load_content('intro.md', 'intro.html')

    output('index.html', template('index'), {
        :states => states,
        :divisions => divisions,
        :intro => index_intro,
        :news => teaser,
    })

    output('intro.html', intro, {}, {:title => "Introduction"})
    output('news.html', template('news'), { :posts => posts },
        {:title => "News"})

    divisions.each do |division_id, division|
        if division['state'].match /t$/ then
            state_or_territory = 'territory'
        else
            state_or_territory = 'state'
        end

        output(File.join('division', "#{division_id}.html"),
               template('division'), {
            :division => division,
            :representative => representatives["division/#{division_id}"],
            :senators => senators[division['state']],
            :state_or_territory => state_or_territory,
            :parties => parties,
            :candidates => candidates_reps["division/#{division_id}"] || [],
        }, {:title => division['name']})
    end

    ['css', 'images', 'js'].each do |dir|
        outdir = File.join(OUTPUT_DIR, dir)
        if Dir.exists?(outdir)
            FileUtils.rm_r(File.join(OUTPUT_DIR, dir))
        end
        FileUtils.cp_r(dir, File.join(OUTPUT_DIR, dir))
    end
end

task :upload => [:site] do
    storage = Fog::Storage.new(:provider => 'Rackspace', :rackspace_region => :syd)
    directory = storage.directories.get "live"
    if directory == nil
        directory = storage.directories.create :key => "live"
    end

    Find.find(OUTPUT_DIR) do |f|
        next if File.directory?(f)

        path = Pathname.new(f).relative_path_from(Pathname.new(OUTPUT_DIR)).to_s
        puts "Uploading #{path}..."
        file = directory.files.create :key => path, :body => File.open(f)
    end

    directory.metadata["Web-Index"] = 'index.html'
    directory.save
end
