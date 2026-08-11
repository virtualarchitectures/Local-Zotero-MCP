# Browsing collections, tags, groups, and other views

## Contents
- Collections and subcollections
- Tags
- Groups
- Trash and My Publications
- Item types

## Collections and subcollections

```
list_collections(top_level_only=True)          # top-level collections only
list_collections()                              # all collections, flat
get_collection(collection_key)                  # a single collection's data
get_subcollections(collection_key)              # direct children of a collection
get_collection_items(collection_key)             # items in a collection
get_collection_items(collection_key, top_level_only=True)  # exclude notes/attachments
get_collection_tags(collection_key)              # tags used within a collection
```

Zotero collections can be nested arbitrarily deep. `list_collections()` returns a flat list with
each collection's `parentCollection` field, so build a tree from that if the user wants a full
hierarchy view rather than calling `get_subcollections` recursively for a deep tree — one flat
call is cheaper than many recursive ones.

## Tags

```
list_tags()                       # every tag in the library
list_tags(filter="method")        # substring-filtered
get_item_tags(item_key)           # tags on one item
get_collection_tags(collection_key)  # tags used within a collection
```

Tags are a good way to explore how a user has organized their own library — e.g. a "to-read" or
"seminal" tag convention. Check `list_tags()` before assuming a tag exists.

## Groups

```
list_groups()
```

Returns group libraries synced locally. Pass a group's `id` as the `library` argument to any
other tool to read that group's library instead of the personal one.

## Trash and My Publications

```
list_trashed_items()      # items in the trash
list_publications()       # items in "My Publications" (personal library only, no `library` param)
```

## Item types

```
get_item_types()
```

Returns every item type Zotero supports (e.g. `"journalArticle"`, `"book"`, `"thesis"`), for use
as the `item_type` filter in `search_items` or `list_collections`-style filtering.
