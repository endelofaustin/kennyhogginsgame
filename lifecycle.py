# LifeCycleManager
#
# Manage different types of game objects that needed to be created and destroyed
# en masse.
#
# UNDYING -- These objects are created programmatically when the game
# starts and are never destroyed until the game ends. Examples -- Player object,
# Editor object.
#
# PER_MAP -- These objects are belong to a map. They can be created
# when the map loads or on the fly. They are destroyed when the map unloads.
class LifeCycleManager:

    # static method to init all lifecycle-managed sets of objects
    def init():
        LifeCycleManager.ALL_SETS = {
            'UNDYING': LifeCycleManager(),
            'PER_MAP': LifeCycleManager()
        }

    # static method to add new objects requested to be added to
    # the event loop, drop and destroy old objects, and process
    # all updates by calling each object's updateloop() function
    def processUpdates(dt):

        for manager in LifeCycleManager.ALL_SETS.values():

            # it's possible to see both an add request and
            # a drop request for the same object in one
            # update cycle. in that case we assume
            # the drop request should have final say, so we
            # process the add and then the drop before ever
            # calling update, so the object that was added
            # and then immediately dropped will never have
            # its update func called.

            # process adds
            for add_me in manager.to_be_added:
                manager.objects.add(add_me)
            manager.to_be_added.clear()

            # process drops
            for delete_me in manager.to_be_dropped:
                manager.objects.discard(delete_me)
                if hasattr(delete_me, 'on_finalDeletion'):
                    delete_me.on_finalDeletion()
            manager.to_be_dropped.clear()

            # process updates
            for obj in manager.objects:
                obj.updateloop(dt)

    # static method to drop all the objects from a given set
    def dropAllObjects(set_name):
        if set_name in LifeCycleManager.ALL_SETS:
            for object in LifeCycleManager.ALL_SETS[set_name].objects:
                if hasattr(object, 'on_finalDeletion'):
                    object.on_finalDeletion()
            LifeCycleManager.ALL_SETS[set_name].objects.clear()
            LifeCycleManager.ALL_SETS[set_name].to_be_added.clear()
            LifeCycleManager.ALL_SETS[set_name].to_be_dropped.clear()

    def __init__(self) -> None:
        self.objects = set()
        self.to_be_added = set()
        self.to_be_dropped = set()

    def addGameObject(self, object):
        self.to_be_added.add(object)

    def dropGameObject(self, object):
        if object in self.objects:
            self.to_be_dropped.add(object)
        self.to_be_added.discard(object)

# GameObject is any object that needs its lifecycle to be managed and updated.
# Other classes should inherit this class so that they will be automatically
# managed. They should call super().destroy() when being destroyed so that
# the object gets removed before the next update loop but after all other
# updates are complete.
class GameObject:

    def __init__(self, lifecycle_manager='PER_MAP') -> None:
        if lifecycle_manager in LifeCycleManager.ALL_SETS:
            self.lifecycle_manager = LifeCycleManager.ALL_SETS[lifecycle_manager]
            self.lifecycle_manager.addGameObject(self)

    def destroy(self):
        self.lifecycle_manager.dropGameObject(self)

    # on_finalDeletion should be implemented in the child class if the
    # object has cleanup to be done -- such as pyglet sprite delete
