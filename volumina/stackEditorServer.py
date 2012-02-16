#!/usr/bin/python

# The VoluminaTileServer is a proof-of-concept demonstrating how to
# serve tiles to be consumed and displayed by CATMAID

# Requirements:
# sudo pip install tornado

from PyQt4.QtCore import QRect, QIODevice, QBuffer

import tornado.ioloop
import tornado.web
import numpy as np

def qimage2str( qimg, format = 'PNG' ):
    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)
    qimg.save(buffer, format)
    data = buffer.data() # type(data) == QByteArray
    buffer.close()    
    # extracts Python str from QByteArray    
    return data.data()


# This handler serves tiles from e.g. volumina
class TileHandler(tornado.web.RequestHandler):
	
	def initialize(self, stackedImageSources):
            self._stackedIms = stackedImageSources
		
	def get(self):
		print "the get request", self.request
		
		# parse the arguments
		#z=self.get_argument('z')
        # the usable parameters posted are:
        # x, y, dx : tileWidth, dy : tileHeight,
        # scale : scale, // defined as 1/2**zoomlevel
        # z : z
        # everything in bitmap pixel coordinates
		
		# create an example PNG
		qimg = self._stackedIms.getImageSource(0).request(QRect(0,0,255,255)).wait()
		self.set_header('Content-Type', 'image/png') 
		self.write(qimage2str(qimg))
		self.flush()
        
	def post(self):
		print "the post request", self.request
		self.write("hello post")

# This handler manages POST request from the canvas label painting
class LabelUploader(tornado.web.RequestHandler):
	
	def post(self):
		datauri = self.get_argument('data')[0]
		output = open('output.png', 'wb')
		output.write(datauri.decode('base64'))
		output.close()
		self.write("success")
	


if __name__ == "__main__":
    import numpy as np
    from pixelpipeline.datasources import ArraySource
    from volumina.layer import GrayscaleLayer
    from volumina.stackEditor import StackEditor
    data = np.random.random_integers(0,255, size= (512,512,128))
    data = data[np.newaxis, ..., np.newaxis]
    ds = ArraySource(data)
    
    se = StackEditor()
    se.layerStackModel.append(GrayscaleLayer(ds))

    VoluminaTileServer = tornado.web.Application([
		    (r"/", TileHandler, {'stackedImageSources': se.imagePump.stackedImageSources}),
		    (r"/labelupload", LabelUploader),
		    ])


    VoluminaTileServer.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
