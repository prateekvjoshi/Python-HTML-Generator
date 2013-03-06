""" 
 
Generating HTML files within Python. For all the Pythonistas out there, you don't have to learn anything new to generate HTML files!
    
This is inspired by James Casbon's recipe: https://gist.github.com/1461441
Extended by Pavlos
    
Very useful in situations requiring generation of HTML within python code. Nothing new to learn, does not 'invent' new language or DSL and as pythonic as it can be.
    
"""

from string import Template


TAB = "  "



class T(object):
    
    """ A template object has a name, attributes and content.
        
        The contents may contain sub template objects.
        
        Attributes are kept in order.
        
        The only things one has to remember:
        
        * Attributes clashing with python keywords must be suffixed with a '_'.
        
        * Attribute names should not start with an underscore '_'
        
        * use the '<' operator to add content to a template object.
        
        """
    
    def __init__(self, name = None):
        self.__name = name
        self.__multi_line = False
        self.__contents = []
        self.__attributes = []
    
    
    def __open(self, level = -1, **namespace):
        out = ["{0}<{1}".format(TAB * level, self.__name)]
        for (name, value) in self.__attributes:
            out.append(' {0}="{1}"'.format(name, value))
        out.append(">")
        
        if self.__multi_line:
            out.append("\n")
        
        templ = ''.join(out)
        
        txt = Template(templ).substitute(namespace)
        
        return txt
    
    
    def __close(self, level = -1, **namespace):
        
        if self.__multi_line:
            txt = "\n{0}</{1}>\n".format(TAB * level, self.__name)
        else:
            txt = "</{0}>\n".format(self.__name)
        return txt

    
    # public API
    
    def _render(self, level = -1, **namespace):
        
        out = []
        
        out_contents = []
        
        contents = self.__contents
        
        for item in contents:
            if item is None:
                continue
            if type(item) is T:
                self.__multi_line = True
                out_contents.append(item._render(level = level + 1, **namespace))
            else:
                out_contents.append("{0}{1}".format(TAB * level, Template(item).substitute(namespace)))
        
        txt_contents = ''.join(out_contents)
        
        if not self.__multi_line:
            txt_contents = txt_contents.strip()
        else:
            txt_contents = txt_contents.rstrip()

        if self.__name:
            out.append(self.__open(level, **namespace))
            out.append(txt_contents)
            out.append(self.__close(level, **namespace))
        else:
            out.append(txt_contents)

        return ''.join(out)

    
    def __getattr__(self, name):
        t = self.__class__(name)
        self < t
        return t
    
    
    def __setattr__(self, name, value):
        if name.startswith('_'):
            self.__dict__[name] = value
        else:
            ## everything else is an element attribute
            ## strip trailing underscores
            self.__attributes.append((name.rstrip('_'), value))


    def _set(self, name, value):
        
        """ settings of attributes when attribure name is not a valid python
            identifier.
            
            """
        
        self.__attributes.append((name.rstrip('_'), value))

    
    def __lt__(self, other):
        self.__contents.append(other)
        return self
    
    
    
    def __call__(self, _class = None, _id = None):
        if _class:
            self.__attributes.append(('class', _class))
        if _id:
            self.id = _id
        
        return self

    
    ## with interface
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        return False





def example():
    
    doc = T()
    doc < """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        \n"""
    
    
    ## we can create a second template object and add it to any other template object.
    
    footer = T()
    with footer.div('footer', 'foot1').h3.p.pre as pre:
        pre.style = 'some style'
        pre < 'This is the footer'
    
    
    with doc.html as html:
        
        with html.head as head:
            ## element attributes are set the usual way.
            head.title = 'Good morning ${name}!'
        
        with html.body as body:
            
            ## there is no need to use the with statement. It is useful for
            ## provide=ing structure and clarity to the code.
            
            body.h3('main') < "Header 3"
            
            ## with statement
            with body.p as p:
                p.class_ ="some class"
                p < "First paragraph"
            
            ## same as above but without the 'with' statement
            body.p("some class") < "Bullet points"
            
            
            with body.ul as ul:
                for i in range(10):
                    ul.li < str(i)
            
            with body.p as p:
                p < "Inline html works fine"
                p.b("bold")
            
            ## append a template object
            body < footer
    
    return doc



if __name__ == "__main__":
    
    doc = example()
    html = doc._render(name = 'Clio')
    print html
