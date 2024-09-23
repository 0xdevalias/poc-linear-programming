# poc-linear-programming

Proof of Concept (PoC) code/notes exploring using linear programming and similar for optimisation.

<!-- TOC start (generated with https://bitdowntoc.derlin.ch/) -->
- [Usage](#usage)
- [See Also](#see-also)
  - [My Other Related Deepdive Gist's and Projects](#my-other-related-deepdive-gists-and-projects)
<!-- TOC end -->

## Usage

First time setup:

```shell
⇒ pyenv virtualenv 3.10.2 poc-linear-programming

⇒ pyenv local poc-linear-programming

⇒ pip install -r requirements.txt
```

Main:

```shell
⇒ python -m optimize_bottles_min_leftover_units_or_cost -h
usage: optimize_bottles_min_leftover_units_or_cost.py [-h] [--min-stacks MIN_STACKS] [--max-stacks MAX_STACKS] [--mode {leftover_units,leftover_units_cost}]

Optimize supplement purchasing strategy.

options:
  -h, --help            show this help message and exit
  --min-stacks MIN_STACKS
                        Minimum number of stacks (default: 7 * 4 days)
  --max-stacks MAX_STACKS
                        Maximum number of stacks (default: 7 * 4 * 2 days)
  --mode {leftover_units,leftover_units_cost}
                        Optimization mode: 'leftover_units' or 'leftover_units_cost' (default: 'leftover_units_cost')
```

Other/legacy:

```shell
# Seemingly not super useful
python -m optimize_bottles_min_leftover_units_constrain_usage_pct

# Legacy
python -m legacy.lcm_bottles
python -m legacy.lcm_bottles_with_max
python -m legacy.optimize_supplements_w1_max_stacks_constrain_usage_pct
python -m legacy.optimize_supplements_w1_max_stacks_constrain_usage_pct_last_bottle
python -m legacy.optimize_supplements_w2_max_stacks_min_leftovers
python -m legacy.optimize_supplements_w2_max_stacks_min_leftovers_constrain_weekly
python -m legacy.optimize_supplements_w3_max_stacks_min_leftover_cost_min_total_cost
python -m legacy.optimize_supplements_w3_max_stacks_min_leftover_cost_min_total_cost_constrain_usage_pct
python -m legacy.optimize_supplements_w3_max_stacks_min_leftovers_min_total_cost
```

## See Also

### My Other Related Deepdive Gist's and Projects

- [Linear Programming, Optimisation Problems, etc (0xdevalias gist)](https://gist.github.com/0xdevalias/b7ec3eba3d6173c279b3e9ee7068bc4b#linear-programming-optimisation-problems-etc)
