# A sample Guardfile
# More info at https://github.com/guard/guard#readme

ignore! /site/

guard 'rake', task: 'content' do
  watch(%r{templates/.+})
  watch(%r{content/.+})
  watch(%r{data/.+})
end

guard 'rake', task: 'js' do
  watch(%r{js/.+})
  watch(%r{vendor/.+\.js})
end

guard 'rake', task: 'css' do
  watch(%r{\.less})
end

guard 'livereload' do
  watch(%r{site/.+})
end

