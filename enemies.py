#!/bin/bash

import pyglet
from decimal import Decimal
from engineglobals import EngineGlobals
from bullet import Bullet
from physics import *

class Enemy(PhysicsSprite):
    
    def __init__(self,):

        PhysicsSprite.__init__(self, has_gravity=True, resource_image_dict={
            'left': pyglet.resource.image("mrspudl.png",),
        })
    
        

