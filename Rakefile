require 'fileutils'
require 'find'
require 'json'
require 'pathname'

require 'fog'
require 'haml'

OUTPUT_DIR = 'site'
TEMPLATE_DIR = 'templates'
DATA_DIR = File.join(OUTPUT_DIR, 'data')

task :output_dirs do
    FileUtils.mkdir_p(OUTPUT_DIR)
    FileUtils.mkdir_p(DATA_DIR)
    FileUtils.mkdir_p(File.join(DATA_DIR, 'division'))
    FileUtils.mkdir_p(File.join(DATA_DIR, 'senators'))
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

task :site => [:output_dirs, :data] do
    Find.find(TEMPLATE_DIR) do |f|
        next if File.directory?(f)

        path = Pathname.new(f).relative_path_from(Pathname.new(TEMPLATE_DIR)).to_s

        template = Haml::Engine.new(File.read(f))
        outpath = File.join(FileUtils.split_all(f).slice(1))
        outpath.sub! /\.haml$/, '.html'
        File.write(File.join(OUTPUT_DIR, outpath), template.render())
    end

    ['images', 'js'].each do |dir|
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
