# Tools and Validation helpers

## Definition of templates

Use the dedicated helpers in `tools/` to verify that templates and RDF files
follow Scriptum's conventions before running the generators:

```
python tools/check_docx.py path/to/template.docx
python tools/check_pptx.py path/to/template.pptx
python tools/check_rdf.py path/to/data.rdf
```

Pass `--debug` to any checker to display the verbose parser output if additional
context is required. The DOCX and PPTX scripts rely on `python-docx` and
`python-pptx`; install them as described in `AGENTS.md` when validating DOCX or
PPTX files.

## Convert video files and generate poster_frame_images

Use `tools/convert_video.py` to convert video files to PowerPoint-friendly MP4 files.

```
python tools/convert_video.py video_file.xxx
```

The script relies on `ffmpeg` and is able to convert 
 `avi`, `mkv`, `mov`, `mpg`, `mpeg`, `wmv`, `flv`, `webm`, `m4v`, `gif`, `qt`, `3gp`

It creates a "poster_frame_image" which is required when adding a video using `python-pptx`:

```
add_movie(movie_file: str | IO[bytes], left: Length, top: Length, width: Length, height: Length, poster_frame_image: str | IO[bytes] | None = None, mime_type: str = 'video/unknown')
```

and implemented in `rdf`:

```
.video:general=file:harmonic.mp4+image:poster=file:harmonic.jpg
```
