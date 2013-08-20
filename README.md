# Below The Line

Welcome to the source code for http://belowtheline.org.au/.

All bug reports and contributions will be gratefully accepted.

If you'd like to add candidates, please check out the format in the
data/people directory. In short, for House of Representatives candidates,
each file is a JSON structure of the format:

```
{
    "first_name": "First",
    "last_name": "Last",
    "candidate": "division/foo",
    "party": "pty"
}
```

The division code and party code can be found by looking in the data/division
and data/party directories. The file naming structure is reasonably clear. If
a candidate doesn't fit the common two-name format, get in touch.

Senate candidates look mostly the same but with an additional ballot_position
item and their candidate item refers to a state rather than a division:

```
{
    "first_name": "First",
    "last_name": "Last",
    "ballot_position": 1,
    "candidate": "state/foo",
    "party": "pty"
}
```

Candidates can also have website links and Wikipedia links by adding "website"
and "wikipedia" items.

Lastly, parties look like this:

```
{
    "name": "The Party Party",
    "code": "PTY",
    "website": "http://partyparty.org.au/"
}
```

If you're adding a party, make sure the code isn't already taken.

## Development

  1. Install Ruby 2.0 & node.js
  1. Install the bundler gem: `gem install  bundler`
  1. Run `bundle install`
  1. Install `lessc`: `npm install -g lessc`
  1. Run `rake site`
  1. Run `rake serve`
  1. Visit [http://localhost:8000](http://localhost:8000)

## License & Copyright

Except where otherwise stated, all code and content is:

Copyright &copy; 2013 Benno Rice & Michael Pearson

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Contact

Any further queries, please contact me at benno@jeamland.net.
