#!/usr/bin/env ruby

require 'json'
require 'haml'
require 'fileutils'

directories = %w{division}
directories.each { |dir| FileUtils.mkdir_p("output/#{dir}") }

states = JSON.load(File.open('data/states.json'))
divisions = JSON.load(File.open('data/divisions.json'))
representatives = JSON.load(File.open('data/house_of_representatives.json'))
senators = JSON.load(File.open('data/senate.json'))

div_by_state = {}

divisions.each do |key, div|
  div['id'] = key

  div_by_state[div['state']] ||= []
  div_by_state[div['state']] << div
end

index = Haml::Engine.new(File.open('templates/index.haml').read)
locals = {states: states, divisions: div_by_state}

File.write('output/index.html', index.render(Object.new, locals))

division = Haml::Engine.new(File.open('templates/division.haml').read)
divisions.each do |key, div|
  locals = div.clone.merge(
    states: states, rep: representatives[key], senators: senators[div['state']]
  )
  File.write("output/division/#{key}.html", division.render(Object.new, locals))
end
