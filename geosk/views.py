from django.shortcuts import render
from geosk.osk import models, utils


def home(request):
    cat = models.Sensor.objects.sos_catalog
    cap = cat.get_capabilities()
    cap = utils.todict(cap)
    sensors = cat.get_sensors(full=False)
    return render(request, 'site_index.html', {
          'sensors': {
              'count': len(sensors)
          }
        }
    )
