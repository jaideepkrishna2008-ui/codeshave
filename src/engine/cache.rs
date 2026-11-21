use std::collections::HashMap;
use std::time::Duration;

pub struct CacheEngine<K, V> {
    store: HashMap<K, V>,
    ttl: Duration,
}

impl<K: std::hash::Hash + Eq, V: Clone> CacheEngine<K, V> {
    pub fn new(ttl: Duration) -> Self {
        CacheEngine {
            store: HashMap::new(),
            ttl,
        }
    }

    pub fn insert(&mut self, key: K, value: V) {
        println!("Storing item in memory cache...");
        self.store.insert(key, value);
    }

    pub fn get(&self, key: &K) -> Option<V> {
        self.store.get(key).cloned()
    }
}
