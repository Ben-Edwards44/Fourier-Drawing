import math
    

class ComplexNum:
    def __init__(self, r, theta):
        self.r = r
        self.theta = theta

    def __mul__(self, other_complex):
        new_r = self.r * other_complex.r
        new_theta = self.theta + other_complex.theta

        return ComplexNum(new_r, new_theta)
    
    def __add__(self, other_complex):
        new_real = self.get_real() + other_complex.get_real()
        new_imaginary = self.get_imaginary() + other_complex.get_imaginary()

        return NonExpComplexNum(new_real, new_imaginary)
    
    def scalar_mult(self, scalar):
        new_r = self.r * scalar

        return ComplexNum(new_r, self.theta)
    
    def get_real(self):
        return self.r * math.cos(self.theta)
    
    def get_imaginary(self):
        return self.r * math.sin(self.theta)
    

class NonExpComplexNum(ComplexNum):
    def __init__(self, real, imaginary):
        r = math.sqrt(real * real + imaginary * imaginary)
        theta = math.atan2(imaginary, real)

        super().__init__(r, theta)
    

class Component:
    def __init__(self, n, cn):
        self.n = n
        self.coefficient = cn

        self.theta_mult = self.n * 2 * math.pi

    def evaluate(self, t):
        theta = self.theta_mult * t
        base_term = ComplexNum(1, theta)

        return self.coefficient * base_term
    
    def get_real(self, t):
        value = self.evaluate(t)

        return value.get_real()
    
    def get_imaginary(self, t):
        value = self.evaluate(t)

        return value.get_imaginary()


def get_coefficient(samples, t_step, n):
    terms = []
    theta_mult = -n * 2 * math.pi
    for i, ft in enumerate(samples):
        t = i * t_step
        multiplier = ComplexNum(1, theta_mult * t)
        term = ft * multiplier

        terms.append(term)

    #use trapezium rule to approximate integral
    cn = ComplexNum(0, 0)
    for i, x in enumerate(terms):
        if i == 0:
            continue

        sum_terms = x + terms[i - 1]
        area_trapezium = sum_terms.scalar_mult(0.5 * t_step)

        cn = cn + area_trapezium

    return cn


"""
samples = []
for i in range(100):
    t = i / 100
    c = ComplexNum(math.cos(2 * math.pi * t), 0)
    samples.append(c)


coef = get_coefficient(samples, 1 / 100, -1)

print(coef.r, coef.theta)
"""


def convert_samples(x_samples, y_samples):
    complex_samples = []
    for x, y in zip(x_samples, y_samples):
        complex_samples.append(NonExpComplexNum(x, y))

    return complex_samples


def fourier_transform(x_samples, y_samples, num_coeffs):
    samples = convert_samples(x_samples, y_samples)
    t_step = 1 / len(samples)

    comps = []
    for n in range(-num_coeffs // 2, num_coeffs // 2):
        cn = get_coefficient(samples, t_step, n)
        component = Component(n, cn)

        comps.append(component)

    return comps