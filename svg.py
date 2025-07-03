SAMPLES_PER_COMP = 100


lerp = lambda a, b, t: a + (b - a) * t
lerp_points = lambda a, b, t: (lerp(a[0], b[0], t), lerp(a[1], b[1], t))

convert_to_abs = lambda point, current_point: [i + x for i, x in zip(point, current_point)]


def read_file(filename):
    with open(filename, "r") as file:
        data = file.read()

    return data


def extract_path(filename):
    lines = read_file(filename).splitlines()

    for i in lines:
        if "path" in i:
            path_line = i
            break

    path_data = ""
    start_adding = False
    for char in path_line:
        if char == '"' or char == "'":
            start_adding = not start_adding
        elif start_adding:
            path_data += char

    return path_data


def sample_func(func, num_samples):
    t_step = 1 / num_samples

    samples = []
    for i in range(num_samples):
        t = i * t_step
        samples.append(func(t))
    
    return samples


def bezier_curve(points, t):
    if len(points) == 2:
        return lerp_points(points[0], points[1], t)
    
    new_points = []
    for i, x in enumerate(points):
        if i == 0:
            continue

        new_point = lerp_points(points[i - 1], x, t)
        new_points.append(new_point)

    return bezier_curve(new_points, t)


def extract_nums(svg_string, start_inx):
    nums = []
    current_num = ""

    for i in svg_string[start_inx + 1:]:
        if i in "0123456789.-":
            current_num += i
        elif i == " " or i == ",":
            if current_num != "":
                nums.append(float(current_num))
                current_num = ""
        else:
            break

    if current_num != "":
        nums.append(float(current_num))

    return nums


def get_coords(svg_string, start_inx, relative_coords, current_point):
    nums = extract_nums(svg_string, start_inx)
    coords = [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]

    curve_type = svg_string[start_inx].lower()

    points = []
    points_on_curve = 0  #as the current point will be on curve already
    for coord in coords:
        if relative_coords:
            coord = convert_to_abs(coord, current_point)

            #chaining with relative coords is weird
            if (curve_type == "c" and points_on_curve % 3 == 2
             or curve_type == "q" and points_on_curve % 2 == 1
             or curve_type == "l"):
                current_point = coord

        points.append(coord)
        points_on_curve += 1

    return points


def run_line(svg_string, start_inx, current_point, relative_coords):
    end_points = get_coords(svg_string, start_inx, relative_coords, current_point)

    samples = []
    for end_point in end_points:
        samples += sample_func(lambda t: lerp_points(current_point, end_point, t), SAMPLES_PER_COMP)
        current_point = end_point

    return samples


def run_return_start(start_point, current_point):
    samples = sample_func(lambda t: lerp_points(current_point, start_point, t), SAMPLES_PER_COMP)

    return samples


def run_horizontal_line(svg_string, start_inx, current_point, relative_coords):
    nums = extract_nums(svg_string, start_inx)
    end_x = nums[0]

    if relative_coords:
        end_x = current_point[0] + end_x

    samples = sample_func(lambda t: lerp_points(current_point, (end_x, current_point[1]), t), SAMPLES_PER_COMP)

    return samples


def run_vertical_line(svg_string, start_inx, current_point, relative_coords):
    nums = extract_nums(svg_string, start_inx)
    end_y = nums[0]

    if relative_coords:
        end_y = current_point[1] + end_y

    samples = sample_func(lambda t: lerp_points(current_point, (current_point[0], end_y), t),SAMPLES_PER_COMP)

    return samples


def run_move(svg_string, start_inx, current_point, relative_coords):
    coords = extract_nums(svg_string, start_inx)

    if relative_coords:
        coords = convert_to_abs(coords, current_point)

    return coords


def run_curve(svg_string, start_inx, current_point, relative_coords):
    points = [current_point] + get_coords(svg_string, start_inx, relative_coords, current_point)

    num_chained_curve = len(points) // 2

    samples = sample_func(lambda t: bezier_curve(points, t), SAMPLES_PER_COMP * num_chained_curve)

    return samples


def generate_samples(svg_string):
    samples = []
    current_point = (0, 0)
    for i, x in enumerate(svg_string):
        relative_coords = x.islower()

        if x in "Mm":
            samples.append(run_move(svg_string, i, current_point, relative_coords))
        elif x in "CcQq":
            samples += run_curve(svg_string, i, current_point, relative_coords)
        elif x in "Ll":
            samples += run_line(svg_string, i, current_point, relative_coords)
        elif x in "Hh":
            samples += run_horizontal_line(svg_string, i, current_point, relative_coords)
        elif x in "Vv":
            samples += run_vertical_line(svg_string, i, current_point, relative_coords)
        elif x in "Zz":
            #samples += run_return_start(samples[0], current_point)
            pass
        elif x not in "0123456789.-, ":
            raise Exception(f"Unsupported svg command: {x}")
        
        if x not in "Zz":
            current_point = samples[-1]

    return samples


def clean_samples(x_samples, y_samples, scale):
    cent_x = x_samples[0] * scale
    cent_y = y_samples[0] * scale

    cleaned_x = []
    for i in x_samples:
        centered = i * scale - cent_x
        cleaned_x.append(centered)

    cleaned_y = []
    for i in y_samples:
        centered = i * scale - cent_y
        cleaned_y.append(centered)

    return cleaned_x, cleaned_y


def parse_svg(filename, scale):
    svg_string = extract_path(filename)
    samples = generate_samples(svg_string)

    x_samples = [i[0] for i in samples]
    y_samples = [i[1] for i in samples]

    return clean_samples(x_samples, y_samples, scale)