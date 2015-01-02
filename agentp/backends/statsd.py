try:
    import statsd
except ImportError:
    print("Before using statsd backend install python package 'statsd':\n\t* pip install statsd\n")
    raise SystemExit(1)

