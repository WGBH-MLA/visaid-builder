# Visaid Builder
Routines for processing MMIF files to create visual indexes ("visaids"), cataloging aid ("cataids"), and other useful output.

These routines require existing MMIF files containing annotations of videos.  MMIF files with relevant annotations can be created with the [CLAMS scenes-with-text detection app](https://github.com/clamsproject/app-swt-detection).

## Overview

### Artifact creation

The primary role of this package is to create artifacts like cataids from MMIF files and the associated video files.

The `use_swt` module is a stand-alone (not presupposing any particular workflow or media source) application for creating visaids from an existing MMIF file and the corresponding media file.

The `process_swt` module includes functions for processing MMIF produced by the [CLAMS swt-detection app](https://github.com/clamsproject/app-swt-detection).

The `post_proc_item` module includes functions called by `run_job` from [CLAMS Kitchen](https://github.com/WGBH-MLA/clams-kitchen) and calls functions in `process_swt` to perform postprocessing on MMIF produced by swt-detection, optinally followed by `create_visaid` or `create_cataid` to construct the relevant artifacts.

### Cataid output procesing (out the cat door)

This package also has functions for analyzing and manipulaing the JSON files yielded by human engagement with a cataid.  This functionallity is defined in the modules in the `catdoor` directory.

## Installation

To install the necessary dependencies, navigate to the project's root directory and run:

```bash
pip install .
```

## Usage

### CLI

For guidance on usage of the stand-alone CLI, run `visswt -h`.

To see a list of the TimeFrame annotations in a MMIF file from SWT-detection, run:
```bash
visswt -d my_swt_output.mmif
```

To create a visaid using the sample MMIF file in this repository, download the corresponding [media file](https://drive.google.com/file/d/1-sSZxDUf9ZKCseVL_QBpqwQNAaffXRBu/view?usp=sharing) to the `sample_files` directory. Then run:

```bash
visswt -d -v sample_files/cpb-aacip-4071f72dd46_swt_v72.mmif sample_files/cpb-aacip-4071f72dd46.mp4
```

To perform ETL operations with catout files (as exported by humans from cataids), use the `catdoor` command.  To see available options, run `catdoor -h`.


### Integration of visaid creation in Python projects

The easiest way to integrate visaid creation into another Python project is by importing `proc_visaid` directly from the `visaid_builder` package and calling it. 

For an example, see the `visaid_builder/integration_example.py` file.


## Configuration Parameters

The various modules in `visaid_builder` use default parameter dictionaries that can be overridden when calling their functions.

When Visaid Builder postprocessing is invoked from CLAMS Kitchen, these are the parameters that can be set in a postprocessing dictionary in the job configuration JSON file.  

### MMIF data processing options
These parameters (from `post_proc_item.py` and `proc_swt.py`) control how the raw MMIF data is filtered and transformed before generating outputs.

| Parameter | Type | Meaning | Default Value |
| :--- | :--- | :--- | :--- |
| `name` | string | Name of the post-processing routine as called from CLAMS Kitchen; used for identification and error reporting. | `None` |
| `artifacts` | list | List of artifact types to generate (e.g., `"data"`, `"slates"`, `"reps"`, `"ksl"`, `"visaids"`, `"cataids"`). | `[]` |
| `adj_tfs` | boolean | If `True`, use the adjusted (filtered/subsampled) scene list for creating artifacts. | `True` |
| `prog_start_min` | integer | Earliest valid start time (in ms) for the main program; used for proxy start inference. | `3000` |
| `prog_start_max` | integer | Latest valid start time (in ms) for the main program; used for proxy start inference. | `150000` |
| `slate_rep_max` | integer | Maximum time (in ms) for a valid slate detection; detections later than this are ignored. | `180000` |
| `default_to_none` | boolean | If `True`, processing parameters not explicitly provided are set to `None`. | `True` |
| `include_only` | list | If provided, only scenes with labels in this list will be included in the output. | `None` |
| `exclude` | list | Scenes with labels in this list will be excluded from the output. | `[]` |
| `max_unsampled_gap`| integer | Maximum duration (in ms) allowed between scenes before an "unlabeled sample" is inserted. | `60000` |
| `subsampling` | dictionary | Mapping of scene labels to duration thresholds (in ms). Scenes exceeding their threshold are split. | (See below) |
| `default_subsampling`| integer | Default subsampling threshold (in ms) applied to unspecified scene types. | `30100` |
| `include_first_time`| boolean | Whether to include a "first frame checked" entry at the start of the scene list. | `False` |
| `include_final_time`| boolean | Whether to include a "last frame checked" entry at the end of the scene list. | `False` |

*Subsampling default dictionary:* `{"bars": 120100, "credits": 1900, "chyron": 15100, "person & chyron": 15100, "other text": 4900, "slate": 9900}`

### Cataid options
These parameters (from `create_cataid.py`) control the generation and appearance of the cataid.

| Parameter | Type | Meaning | Default Value |
| :--- | :--- | :--- | :--- |
| `deselected_scene_types` | list | Scene types that are hidden by default in the interactive display. | `["filmed text"]` |
| `job_id_in_cataid_filename` | boolean | Whether to include the Job ID in the generated HTML filename. | `False` |
| `type_signified_in_cataid_filename` | string | A string included in the filename to indicate the output type, usually "cataid" or "visaid". | `"cataid"` |
| `display_video_duration` | boolean | Whether to display the total duration of the video in the header. | `True` |
| `display_job_info` | boolean | Whether to display Job ID and Job Name in the header. | `True` |
| `display_image_ms` | boolean | Whether to display the millisecond timestamp for each image. | `True` |
| `aapb_timecode_link` | boolean | Whether to include links to the AAPB timecode playback for each scene. | `False` |
| `max_img_height` | integer | The maximum display height (in pixels) for images in the layout. | `360` |
| `use_ai_helper` | boolean | Whether to use an AI helper to refine ("catify") extracted text. | `False` |
| `custom_prompt_file` | string | Path to a file containing custom prompts for the AI helper. | `None` |

### Visaid options
These parameters (from `create_visaid.py`) control the generation and appearance of visaid.

| Parameter | Type | Meaning | Default Value |
| :--- | :--- | :--- | :--- |
| `deselected_scene_types` | list | Scene types that are hidden by default in the interactive display. | `["filmed text"]` |
| `job_id_in_visaid_filename` | boolean | Whether to include the Job ID in the generated HTML filename. | `False` |
| `display_video_duration` | boolean | Whether to display the total duration of the video in the header. | `True` |
| `display_job_info` | boolean | Whether to display Job ID and Job Name in the header. | `True` |
| `display_image_ms` | boolean | Whether to display the millisecond timestamp for each image. | `True` |
| `aapb_timecode_link` | boolean | Whether to include links to the AAPB timecode playback for each scene. | `False` |
| `max_img_height` | integer | The maximum display height (in pixels) for images in the layout. | `360` |


