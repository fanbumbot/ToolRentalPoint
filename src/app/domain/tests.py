import unittest
import random

from .entity import Entity, EntityCQImpl

class TestCase(unittest.TestCase):

    def test_entity_equal_int(self):
        entity1 = Entity(30, EntityCQImpl(dict()))
        entity2 = Entity(30, EntityCQImpl(dict()))

        check = entity1 == entity2

        self.assertEqual(check, True)

    def test_entity_not_equal_int(self):
        entity1 = Entity(30, EntityCQImpl(dict()))
        entity2 = Entity(31, EntityCQImpl(dict()))

        check = entity1 == entity2

        self.assertEqual(check, False)

    def test_entity_equal_str(self):
        entity1 = Entity("ABC", EntityCQImpl(dict()))
        entity2 = Entity("ABC", EntityCQImpl(dict()))

        check = entity1 == entity2

        self.assertEqual(check, True)

    def test_entity_not_equal_str(self):
        entity1 = Entity("ABC", EntityCQImpl(dict()))
        entity2 = Entity("CDE", EntityCQImpl(dict()))

        check = entity1 == entity2

        self.assertEqual(check, False)

    def test_entity_hash_int(self):
        entity = Entity(491, EntityCQImpl(dict()))

        hash = entity.__hash__()

        self.assertEqual(hash, 491)

    def test_entity_hash_str(self):
        entity = Entity("test", EntityCQImpl(dict()))

        hash = entity.__hash__()

        self.assertEqual(hash, "test".__hash__())

    def test_entity_dict(self):
        
        entity1 = Entity(10, EntityCQImpl(dict()))
        entity2 = Entity(11, EntityCQImpl(dict()))
        dictionary = dict()
        
        dictionary[entity1] = 1
        dictionary[entity2] = 2
        value1 = dictionary[entity1]
        value2 = dictionary[entity2]

        self.assertEqual(value1, 1)
        self.assertEqual(value2, 2)

    def test_entity_list_count(self):
        all_entities = list()

        for _ in range(20):
            entity = Entity(random.randint(10, 30), EntityCQImpl(dict()))
            all_entities.append(entity)
        
        main_entity = Entity(40, EntityCQImpl(dict()))
        all_entities.append(main_entity)

        count = all_entities.count(main_entity)
        self.assertEqual(count, 1)

    def test_entity_list_index(self):
        all_entities = list()

        for _ in range(20):
            entity = Entity(random.randint(10, 30), EntityCQImpl(dict()))
            all_entities.append(entity)
        
        main_entity = Entity(40, EntityCQImpl(dict()))
        all_entities.append(main_entity)

        index = all_entities.index(main_entity)
        self.assertEqual(index, len(all_entities)-1)
