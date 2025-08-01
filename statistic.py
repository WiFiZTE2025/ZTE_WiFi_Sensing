import time
import threading
from collections import defaultdict, deque, Counter
import numpy as np

class Statistic:
    def __init__(self):
        self.lock = threading.Lock()
        self.metrics = {}

    def register(self, name, stat_type, value_range=None, bins=10):
        with self.lock:
            if stat_type == 'discrete':
                self.metrics[name] = {
                    'type': 'discrete',
                    'all_time': Counter(),
                    'recent': deque()
                }
            elif stat_type == 'integer':
                self.metrics[name] = {
                    'type': "integer",
                    'range': value_range,
                    'bins': bins,
                    'all_time': [],
                    'recent': deque()
                }
            else:
                raise ValueError("stat_type must be 'discrete' or 'integer'")
            
    def record(self,name, value):
        now = time.time()
        with self.lock:
            if name not in self.metrics:
                raise KeyError(f"statistic '{name}' not registered")
            metric = self.metrics[name]
            if metric['type'] == 'discrete':
                metric['all_time'][value] += 1
                metric['recent'].append((now, value))
            elif metric['type'] == 'integer':
                metric['all_time'].append(value)
                metric['recent'].append((now, value))

            cutoff = now - 5
            while metric['recent'] and metric['recent'][0][0] < cutoff:
                metric['recent'].popleft()

    def report(self, name):
        now = time.time()
        with self.lock:
            if name not in self.metrics:
                raise KeyError(f"statistic '{name}' not registered")
            metric = self.metrics[name]
            result = {'name': name, 'type': metric['type']}
            if metric['type'] == 'discrete':
                result['all_time'] = dict(metric['all_time'])
                recent_counts = Counter(v for t, v in metric['recent'])
                result['last_5s'] = dict(recent_counts)
            elif metric['type'] == 'integer':
                data_all = np.array(metric['all_time']) if metric['all_time'] else np.array([])
                data_recent = np.array([v for t,v in metric['recent']]) if metric['recent'] else np.array([])

                result['all_time'] = {
                    'min': float(data_all.min()) if data_all.size else None,
                    'max': float(data_all.max()) if data_all.size else None,
                    'mean': float(data_all.mean()) if data_all.size else None,
                    'hist': np.histogram(data_all, bins=metric['bins'], range=metric['range'])[0].tolist() if data_all.size else []
                }

                result['last_5s'] = {
                    'min': float(data_recent.min()) if data_recent.size else None,
                    'max': float(data_recent.max()) if data_recent.size else None,
                    'mean': float(data_recent.mean()) if data_recent.size else None,
                    'hist': np.histogram(data_recent, bins=metric['bins'], range=metric['range'])[0].tolist() if data_recent.size else []
                }
            return result
    def reset(self, name=None):
        with self.lock:
            if name:
                if name in self.metrics:
                    self.register(name, self.metrics[name]['type'], self.metrics[name].get('range'), self.metrics[name].get('bins', 10))
                else:
                    raise KeyError(f"statistic '{name}' not registered")
            else:
                names = list(self.metrics.keys())
                for name in names:
                    self.register(name, self.metrics[name]['type'], self.metrics[name].get('range'), self.metrics[name].get('bins', 10))