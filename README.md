# World of Food

A small project for teaching myself Python by building something I'd actually
use: a way to keep track of the restaurants I've been to and get new recommendations
for restaurants based on my preferences.

This is a work in progress. Lots of things are missing, nothing is fully polished.
As any side-project, I'm trying not to fall into the trap of optimizing everything up-front
and building all the bells and whistles right away.

## What it does

- Looks up restaurants by cuisine and location, falling back to the Google
  Places API when there isn't enough already saved.
- Lets you log visits — where, when, and how it went.
- Once there's enough visit history, works out which cuisines you keep
  coming back to and recommends things at the price point you usually prefer.

## What it doesn't do but hopefully will one day
- Pairs with a fun UI 
- Builds a smarter profile of your preferences so that all the things that matter to you are
  included, not just basic restaurant parameters.
- Integrate w/ Google Maps to let you post reviews 
- Let you share your world of food with others
- And, of course, all the actually necessary things for a real prod-ready app

## Running it

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs for the interactive API.

You'll need a Google Places API key in `.env.local`:

```
PLACES_API_KEY=your-key-here
```

## Tests

```
pytest
```
