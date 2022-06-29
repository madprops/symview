<img src="https://i.imgur.com/PyXJEqi.jpg" width="350">

# Symbolic Link Snapshots

If you go to a parent directory and run:  
`python /path/to/symview.py images dinosaur`  

It performs a recursive file name search.  
Then it checks the mimetype to check if it's of a certain type.  
All the results (up to a max of 100) will be symlinked to /tmp/symview_results.  
The symlink directory is opened with your file manager.  
Now you have linked files available to view and use.  
It ignores directories with dots at the start.  
It ignores directories and symlinks.

Valid result types: 
* images
* videos
* audio
* media
* all

Fish functions:  

```  
function i
  python /home/yo/code/symview/symview.py images "$argv"
end

function v
  python /home/yo/code/symview/symview.py videos "$argv"
end

function a
  python /home/yo/code/symview/symview.py audio "$argv"
end

function m
  python /home/yo/code/symview/symview.py media "$argv"
end
```