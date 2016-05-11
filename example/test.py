import time
from example.app import User, computed_value

User(name='John Doe').save()

user = User.objects.order_by('-_id').first()

# This first time would take 4 seconds to compute
print "COMPUTING VALUE FOR FIRST TIME..."
print computed_value(user)
print "DONE COMPUTING"

print "UPDATING THE NAME OF JOHN DOE"
user.name = 'John Dee'
user.save()

# At this point Smache has noticed that a cached value needs to be updated.
# We will wait a couple of seconds for it to finish.
print "WAITING FOR WORKER..."
time.sleep(4)
print "TRYING TO COMPUTE AGAIN"

# This is computed instantly since it retreives the value from the cache
print computed_value(user)
