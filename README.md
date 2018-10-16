# Joe Bogan "Botcast"

A toy project that generates "botcasts" from machine-generated text based off of the Joe Rogan Podcast.

### The steps
- Auto-transcribe the podcast audio into text including speech diarization
- Machine learn against the transcribed text, and generate new text
- Train voice models using the podcast
- Synthesize speech and have "Joe Bogan" and guests speak the new generated text

WIP

### Setup
The python environment is managed by [Pipenv](https://github.com/pypa/pipenv). If you have it installed,
just run `pipenv install`

Rename/copy the `config_TEMPLATE.ini` file to `config.ini` file in the root directory
Fill in the username/password generated for your
[IBM Speech-to-text](https://www.ibm.com/watson/services/speech-to-text/) instance (free lite tier is good enough)
