from django import template

register = template.Library()

@register.tag
def cloud_value(parser, token):
    """A wrapper around DataPointsCloud.value_at.
    """
    return CloudValueNode(*cloud_common_parse(parser, token))

@register.tag
def cloud_total(parser, token):
    """A wrapper around DataPointsCloud.sum_.
    """
    return CloudTotalNode(*cloud_common_parse(parser, token))


class BaseCloudFilterNode(template.Node):
    def __init__(self, cloud, keyvalues, var_name):
        self.cloud = template.Variable(cloud)
        self.keyvalues = keyvalues
        self.var_name = var_name
    
    def _normalize(self, arg, context):
        if arg[0] in ('"', "'") and arg[0] == arg[-1]:
            return arg[1:-1]
        return template.Variable(arg).resolve(context)
    
    def _keyvalues(self, context):
        for key, value in self.keyvalues:
            yield str(key), self._normalize(value, context)
    
    def render(self, context):
        cloud = self.cloud.resolve(context)
        keyvalues = dict(self._keyvalues(context))
        
        value = self.cloud_proxy(cloud, keyvalues)
        if self.var_name is None:
            return value
        
        context[self.var_name] = value
        return ''
    
    def cloud_proxy(self, cloud, keyvalues):
        raise NotImplementedError

class CloudValueNode(BaseCloudFilterNode):
    def cloud_proxy(self, cloud, keyvalues):
        return cloud.value_at(**keyvalues)

class CloudTotalNode(BaseCloudFilterNode):
    def cloud_proxy(self, cloud, keyvalues):
        return cloud.sum_(**keyvalues)

def cloud_common_parse(parser, token):
    """{% tag_name cloud k1=v1 k2=v2 ... [as name] %}"""
    content = token.split_contents()
    
    if content[-2] == 'as':
        var_name = content.pop()
        content.pop() # contains "as"
    else:
        var_name = None
    
    cloud = content[1]
    
    keyvalues = [bit.split('=') for bit in content[2:]]
    
    return cloud, keyvalues, var_name
