def read_pos(str):
    try:
        if not str or "," not in str:
            return (0.0, 0.0, 100.0)
        str = str.split(",")
        return (float(str[0]), float(str[1]), float(str[2]))
    except ValueError:
        print(f"Malformed position data: {str}")
        return (0.0, 0.0, 100.0)

def make_pos(tup):
    return f"{tup[0]:.1f},{tup[1]:.1f},{tup[2]:.1f}"