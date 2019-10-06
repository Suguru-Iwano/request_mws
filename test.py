#!/usr/bin/env python3
import reqamz
from wrapmongo import MongoAccess

def main():
    mongo = MongoAccess()
    results = mongo.find(projection={'ASIN':1})
    [print(r) for r in results]


if __name__ == '__main__':
    main()
