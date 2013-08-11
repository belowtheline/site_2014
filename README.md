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

  1. Install Ruby 2.0 & node.js & Python
  1. Install the bundler gem: `gem install  bundler`
  1. Run `bundle install`
  1. Install `lessc`: `npm install -g lessc`
  1. Run `rake site`
  1. Run `rake serve`
  1. Visit [http://localhost:8000](http://localhost:8000)

Any further queries, please contact me at benno@jeamland.net.
