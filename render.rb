#!/usr/bin/env ruby

require 'json'
require 'haml'

directories = [
    'division'
]

if not Dir.exists?("output")
    Dir.mkdir("output")
end

directories.each do |dir|
    dir = "output/#{dir}"
    if not Dir.exists?(dir)
        Dir.mkdir(dir)
    end
end

states = JSON.load(File.open('data/states.json'))
divisions = JSON.load(File.open('data/divisions.json'))
representatives = JSON.load(File.open('data/house_of_representatives.json'))
senators = JSON.load(File.open('data/senate.json'))

div_by_state = {}

divisions.each do |key, div|
    div['id'] = key

    if not div_by_state.has_key?(div['state'])
        div_by_state[div['state']] = []
    end

    div_by_state[div['state']] << div
end

index = Haml::Engine.new(File.open('templates/index.haml').read)
locals = {
    :states => states,
    :divisions => div_by_state,
}
File.open('output/index.html', 'w').write(index.render(Object.new, locals))

division = Haml::Engine.new(File.open('templates/division.haml').read)
divisions.each do |key, div|
    locals = div.clone
    locals['states'] = states
    locals['rep'] = representatives[key]
    locals['senators'] = senators[div['state']]
    html = File.open("output/division/#{key}.html", 'w')
    html.write(division.render(Object.new, locals))
end
