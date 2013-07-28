require 'fileutils'
require 'find'
require 'json'
require 'pathname'

require 'fog'
require 'haml'

OUTPUT_DIR = 'site'
TEMPLATE_DIR = 'templates'

task :output_dirs do
    FileUtils.mkdir_p(OUTPUT_DIR)
    FileUtils.mkdir_p(File.join(OUTPUT_DIR, 'data'))
end

task :data => [:output_dirs] do
    blob = {:state => {}, :division => {}}

    Dir.foreach('data/state') do |name|
        next unless name =~ /\.json$/
        data = JSON.parse(File.read(File.join('data', 'state', name)))
        blob[:state][name.gsub(/\.json$/, '')] = data
    end

    Dir.foreach('data/division') do |name|
        next unless name =~ /\.json$/
        data = JSON.parse(File.read(File.join('data', 'division', name)))
        blob[:division][name.gsub(/\.json$/, '')] = data
    end

    File.write(File.join(OUTPUT_DIR, 'data', 'data.js'),
        "var _btldata = " + JSON.generate(blob) + ";")
end

task :site => [:output_dirs, :data] do
    Find.find(TEMPLATE_DIR) do |f|
        next if File.directory?(f)

        path = Pathname.new(f).relative_path_from(Pathname.new(TEMPLATE_DIR)).to_s

        template = Haml::Engine.new(f)
        File.write(File.join(OUTPUT_DIR, path), template.render())
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
