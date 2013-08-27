require "rubygems"
require "sinatra/base"

require 'bundler/setup'
Bundler.require(:development)

SHORTREV = `git rev-parse --short HEAD`.strip() || 'xxx'

Layout = Haml::Engine.new(File.read(File.join('..', 'templates', 'layout.haml')))
Ballot = Haml::Engine.new(File.read(File.join('..', 'templates', 'ballot.haml')))

class WebBallot < Sinatra::Base

  set :public_folder, File.expand_path('../../site', __FILE__)

  get '/ballot/:ballot_id' do
    locals = {
      base: nil,
      title: 'Ballot',
      shortrev: SHORTREV,
      rollbar_environment: ENV['BTL_PRODUCTION'] ? 'production' : 'debug',
    }

    redis = Redis.new(:db => 5)
    puts redis.hgetall(params[:ballot_id]).inspect

    locals[:body] = Ballot.render()

    return Layout.render(Object.new, locals)
  end

end
