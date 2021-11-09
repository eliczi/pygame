import random
import csv
import copy
from map import TileMap


class Room:
    def __init__(self, x, y):
        self.x = x  # position in game world
        self.y = y
        self.neighbours = []  # neighbouring rooms coordinates
        self.doors = []  # door locations
        self.type = None  # type of the room, to be added
        self.room_map = None  # list of sprite identifiers
        self.room_image = None  # TileMap
        self.discovered = False
        self.enemy_list = [] # list of enemies at that room

    def __repr__(self):
        return f'({self.x}, {self.y}), {self.type}'  # str(self)?

    def __str__(self):
        return self.__repr__()


    def position_to_direction(self, position):
        direction = None
        if position[0] == 1:
            direction = 'up'
        elif position[0] == -1:
            direction = 'down'
        elif position[1] == 1:
            direction = 'left'
        elif position[1] == -1:
            direction = 'right'
        self.doors.append(direction)

    def add_doors(self):
        if len(self.neighbours) == 1:  # if only 1 neighbour, there must be a door to that neighbour
            position = [self.x - self.neighbours[0][0], self.y - self.neighbours[0][1]]
            self.position_to_direction(position)  # add position to door list
        else:
            for neighbour in self.neighbours:
                position = [self.x - neighbour[0], self.y - neighbour[1]]
                self.position_to_direction(position)


def map_generator(num_of_rooms, width, height, spritesheet):
    """Generate specified number of room in a world of specified size and connection between them"""
    world = [[None for x in range(width)] for y in range(height)]
    x, y = random.randint(0, height - 1), random.randint(0, width - 1)

    def check_boundary(x, world_param):  # checks if x doesnt exceed world boundary
        if x >= world_param or x < 0:
            return False
        return True

    def check_free_space():  # returns free neighbouring spaces
        free_space = []
        for i in [-1, 1]:
            if check_boundary(x + i, height) and world[x + i][y] is None:
                free_space.append([x + i, y])
        for q in [-1, 1]:
            if check_boundary(y + q, width) and world[x][y + q] is None:
                free_space.append([x, y + q])
        return free_space

    def reset_world():  # resets game world
        for i in range(height):
            for y in range(width):
                world[i][y] = None

    room_counter = 0
    first_room = True
    start = None
    while room_counter < num_of_rooms:  # this while loop populates game world with one possible room-layout
        if first_room:
            start = world[x][y] = Room(x, y)
            world[x][y].type = 'starting_room'
            world[x][y].discovered = True
            first_room = False
        else:
            world[x][y] = Room(x, y)
        empty_spaces = check_free_space()
        if empty_spaces:
            new_room = random.choice(empty_spaces)
            x, y = new_room[0], new_room[1]
            room_counter += 1
        elif room_counter == width * height - 1:
            break
        else:
            reset_world()
            first_room = True
            room_counter = 0

    def add_neighbors():  # appends neighbours of every room
        for row in world:
            for room in row:
                if isinstance(room, Room):
                    for i in [-1, 1]:  # up/down
                        if check_boundary(room.x + i, height) and world[room.x + i][room.y] is not None:
                            room.neighbours.append([room.x + i, room.y])
                    for q in [-1, 1]:  # left/right
                        if check_boundary(room.y + q, width) and world[room.x][room.y + q] is not None:
                            room.neighbours.append([room.x, room.y + q])
                    room.add_doors()  # generates doors

    def add_room_map():
        with open('../maps/new2_test_map.csv', newline='') as f:  # load room template
            reader = csv.reader(f)
            basic_map = list(reader)

        for row in world:  # make passage through rooms
            for room in row:
                if isinstance(room, Room):
                    room_map = copy.deepcopy(basic_map)  # csv file
                    for door in room.doors:
                        if door == 'left':
                            room_map[5][0] = -1
                            room_map[4][0] = 33
                            room_map[6][0] = 3
                        if door == 'right':
                            room_map[5][12] = -1
                            room_map[4][12] = 33
                            room_map[6][12] = 3
                        if door == 'up':
                            room_map[1][6] = -1
                        if door == 'down':
                            room_map[9][6] = -1
                            room_map[9][5] = 47
                            room_map[9][7] = 45
                    room.room_map = room_map

    def add_graphics():
        for row in world:
            for room in row:
                if isinstance(room, Room):
                    room.room_image = TileMap(room.room_map, spritesheet)

    def print_world():
        for row in world:
            for room in row:
                if isinstance(room, Room):
                    print(1, end=' ')
                else:
                    print(0, end=' ')
            print('')

    def assign_type():
        types = ['power_up', 'normal', 'boss', 'shop']
        for row in world:
            for room in row:
                if isinstance(room, Room) and room.type is None:
                    room.type = random.choices(types, weights=[0.2, 0.6, 0.05, 0.15], k=1)[0]

    assign_type()
    add_neighbors()
    add_room_map()
    add_graphics()
    #print_world()

    return world, start
