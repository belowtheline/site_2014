# A sample Guardfile
# More info at https://github.com/guard/guard#readme

ignore! /site/

guard 'rake', task: 'content', run_on_start: false do
  watch(%r{templates/.+})
  watch(%r{content/.+})
  watch(%r{data/.+})
end

guard 'rake', task: 'js', run_on_start: false do
  watch(%r{js/.+})
  watch(%r{vendor/.+\.js})
end

guard 'rake', task: 'css', run_on_start: false do
  watch(%r{\.less})
end

guard 'livereload' do
  watch(%r{site/.+})
end

