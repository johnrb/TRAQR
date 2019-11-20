## TRAQR Website

#### This repository contains code for building the [website](http://people.goshen.edu/~stu_phys/traqr) of the Goshen College air quality research group.

### Requirements
- jekyll
- ruby

### Testing locally
Run `jekyll server` in the directory where this is stored. 
Make sure `baseurl` and `url` are set to empty strings in `_config.yml`. 

### Uploading
- Make sure `baseurl` and `url` are set properly in `_config.yml`. 
- Compile the site with `jekyll build`.
- Run `push_updates.sh`. This pushes the content of `_site/` to the proper place on the people server.

### To Do
- Disable map buttons if screen too small (mobile)
- Add people page
- Add device page
- [for much later] add pages on the device or other project developments
