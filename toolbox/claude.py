from collections import defaultdict

class Axis(object):
    """An axis is characterized by two properties:
        * A name (more readable than a numerical list index),
        * A projection method that knows how to extract the relevant coordinate
            out of a row object.
    """
    def __init__(self, name, projection=None):
        if projection is None:
            projection = lambda row: getattr(row, name)
        
        self.name = name
        self.projection = projection
    
    def project(self, row):
        """Projects the row object onto the axis.
        Return the coordinate of the given object on the axis.
        Note that coordinates must be hashable objects.
        """
        return self.projection(row)


class DataPointsCloud(object):
    """A N-dimensional system of data points.
    Behind the scene, a defaultdict is used for the storage of points.
    Its default value can be customized in the __init__ method."""
    
    available_axis_lookups = {
        'in': lambda filter, actual: actual in filter,
        'equals': lambda filter, actual: actual == filter,
    }
    
    def __init__(self, axes=None, default_factory=None):
        if not callable(default_factory):
            default_factory = lambda: default_factory
        self._dict = defaultdict(default_factory)
        
        if axes is None:
            axes = []
        self.axes = axes
    
    def points(self, iterable=False):
        """Return all points in the system in the form of (coordinates, value).
        """
        return iterable and self._dict_iteritems() or self._dict.items()
    
    def point_at(self, *args, **kwargs):
        """Return a (coordinate, value) tuple for the point situated
        at the given coordinates.
        Coordinates can be provided in wo ways:
            * If positional arguments are provided, they are interpreted as
            a coordinate tuple, corresponding to the internal representation:
            this require knowledge of the "layout" of the axes
            (namely, the order of the self.axes list).
            * If keyword arguments are provided, they are interpreted as
            names of axes and the corresponding coordinates.
            This is generally what you want to do.
            
        Note that the two different ways cannot be mixed and the method
        will throw an error in this case.
        """
        if args and kwargs:
            raise ValueError # TODO: throw better exception
        
        if kwargs:
            args = self.named_coords_to_tuple(kwargs)
        
        if len(args) != len(self.axes):
            raise ValueError # TODO: throw better exception
        return args, self._dict[args]
    
    def value_at(self, *args, **kwargs):
        """Return the value situated at the given coordinates.
        See docstring on the point_at() method on how to specify coordinates.
        """
        return self.point_at(*args, **kwargs)[1]
    
    def named_coords_to_tuple(self, named):
        """Convert a dict of (name, value) into the tuple that corresponds
        to the internal representation.
        """
        return tuple(named.get(axis.name) for axis in self.axes)
    
    def get_axis_index(self, axis_name):
        """Return the internal index of the axis with the given name.
        """
        correspondance_table = dict((axis.name, i) for i, axis in enumerate(self.axes))
        return correspondance_table.get(axis_name)
    
    def load_data(self, data, make_point=None):
        """Load data from an iterable into the internal representation."""
        if make_point is None:
            make_point = lambda row, current: row

        for row in data:
            coordinates = tuple(axis.project(row) for axis in self.axes)
            current_value_at_point = self.value_at(*coordinates)
            self._dict[coordinates] = make_point(row, current_value_at_point)
    
    def points_at(self, **filters):
        """Return points matching the criteria given by the filters keywords.
        See note on XXX for the syntax of filters."""
        filter_callback = lambda point: self.point_match_filters(point, filters)
        return filter(filter_callback, self.points())
    
    def values_at(self, **filters):
        """A simple wrapper around self.points_at() to return only the values.
        """
        return [p[1] for p in self.points_at(**filters)]
    
    def sum_(self, **filters):
        """A utility method to sum values of points matching a criteria."""
        return sum(self.values_at(**filters))
    
    def point_match_filters(self, point, filters):
        """Return whether the given point matches the criteria specified by the filters keywords.
        """
        coordinates = point[0]
        return all(self.test_for_axis(coordinates, *f) for f in filters.items())
    
    def test_for_axis(self, coordinates, axis_name, filter_value):
        """
        """
        if '__' in axis_name:
            axis_name, lookup = axis_name.split('__')
        else:
            lookup = 'equals'
        
        actual_value = coordinates[self.get_axis_index(axis_name)]
        try:
            test_callback = self.available_axis_lookups[lookup]
        except IndexError:
            return False # TODO: Better exception handling
        else:
            return test_callback(filter_value, actual_value)
