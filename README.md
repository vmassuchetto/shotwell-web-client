![Shotwell Web Client screenshot](https://raw.githubusercontent.com/vmassuchetto/shotwell-web-client/master/screenshot.jpg)

A very simple and responsive web client that tries to mimic the Shotwell
interface with infinite scroll and event views. It will connect to the
application's SQLite database to find photos and use the already generated
thumbnails without modifying or creating anything. It streams both photos and
videos.

Uses [Flask](http://flask.pocoo.org), [Bootstrap](http://getbootstrap.com/),
[jQuery](https://jquery.com), [Justified
Gallery](http://miromannino.github.io/Justified-Gallery/) and
[Swipebox](http://brutaldesign.github.io/swipebox/).

## Installation and usage

    pip install git+https://github.com/vmassuchetto/shotwell-web-client.git
    shotwell-web-client

The user that will execute the web server must have access to the database,
photos and thumbnails.

## Configuration

Check the `config.py` file if your Shotwell installation requires different paths.

    DATABASE = "~/.local/share/shotwell/data/photo.db"  # database path
    THUMBPATH = "~/.cache/shotwell/thumbs/"             # thumbnails path
    LOAD = 25                                           # images to load on scroll

## Development

    git clone https://github.com/vmassuchetto/shotwell-web-client.git
    cd shotwell-web-client
    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt
    cd shotwell_web_client
    npm install
    DEBUG=True python run.py

## Additional scripts

* [`shotwell-thumbnailer`](https://gist.github.com/vmassuchetto/1c11a671f890a770a7a030c06d9f1f7e)
  generate missing thumbnails without browsing Shotwell
* [`shotwell-sync-dirs`](https://gist.github.com/vmassuchetto/edad377425c1274cb6f9e432e9a74de2):
  syncronize directory structure of files, moving them to their exposed time
  adjusted on Shotwell
