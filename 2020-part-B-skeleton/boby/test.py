import math


def q_2(db_1):
    db_2 = db_1 + 10*math.log(3, 10)
    return db_2


def q_3(p):
    f = 1/p * 100
    return f


def q_4(angle, n_air=1, n_lamp=1.52, n_rubbing=1.36, n_vegetable=1.49, n_water=1.33, n_dish=1.40):
    degree_in_bottom = math.degrees(math.asin(math.sin(math.radians(4.9))*n_air/n_dish))

    return degree_in_bottom

print(q_2(35.03))

print(q_3(2.70))

print(q_4(4.9))