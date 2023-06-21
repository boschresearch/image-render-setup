
<!---
<LICENSE id="CC BY-SA 4.0">
    
    Image-Render Blender Label add-on module documentation
    Copyright 2022 Robert Bosch GmbH and its subsidiaries
    
    This work is licensed under the 
    
        Creative Commons Attribution-ShareAlike 4.0 International License.
    
    To view a copy of this license, visit 
        http://creativecommons.org/licenses/by-sa/4.0/ 
    or send a letter to 
        Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
    
</LICENSE>
--->
# Label Data Generation

## Custom World Coordinate System

By default all positions and axes in the generated label data, are given relative to the Blender world coordinate system. However, a custom world coordinate system can be defined, by creating an Empty with the name `AT.Label.Orig.World`. If such an Empty is found, all 3d-positions are given in this coordinate system, taking into accound the orientation and position of the Empty.

## Instance handling

Label types are given per collection. Each collection that has a defined label type, can have different instance types, which results in a different assignment of instance indices. In the following, "*valid object*" are objects of types `MESH` or `ARMATURE`. 

In particular, Empties are not regarded as instances and their children are treated as separate objects. However, the children of a `MESH` object are regarded as belonging to the same instance as their parent, recursively. That is, if an instance has as top level element an Empty and all children of this empty should be regarded as a single instance, the whole hierarchy of objects has to be placed in a collection.

- **Single**: All objects and their children and all child collections with their objects are regarded as a single instance.

- **Collection**: All objects in this collection are one instance and all objects in each child collection is one object, recursively. That is, each child collection is treated as if it had instance type 'Single'. The instance orientation of each child collection can be determined by an Empty with a name of the type `[anything];AT.Label.Instance.Orientation`. If no such Empty is given, the first empty in the collection is used. If no Empty is in the collection, the orientation of the first object in the collection is used. If that object has a child Empty that conforms with the instance orientation naming convention, then this empty is used.

- **Object**: Every valid object and its' children are an instances. Uses each object's orientation as instance orientation, or a child orientation empty that has a name of the type `[anything];AT.Label.Instance.Orientation`.

The following table gives a detailed overview of how the instance index is incemented within a collection, depending
on the combination of the parent the collection's and this collection's instance increment types.
This assumes that the label types are the same. 

If the label type of the parent differs from this label type, it has the same effect 
as if the parent had instance increment type "NONE".

| Parent 		| This 			| First Object 	| Next Objects 	| 
| -------		| -----			| ------		| ---------- 	| 
| None			| None	 		| +0			| +0		 	| 
| None			| Single 		| +1			| +0		 	| 
| None			| Collection 	| +1			| +0		 	| 
| None			| Object		| +1			| +1			|
| None			| Inherit		| +0			| +0			|
| | | | | 
| Single		| None	 		| +0			| +0		 	| 
| Single		| Single 		| +0			| +0		 	| 
| Single		| Collection 	| +1			| +0		 	| 
| Single		| Object		| +1			| +1			|
| Single		| Inherit		| +0			| +0			|
| | | | | 
| Collection	| None	 		| +1			| +0		 	| 
| Collection	| Single 		| +1			| +0		 	| 
| Collection	| Collection 	| +1			| +0		 	| 
| Collection	| Object		| +1			| +1			|
| Collection	| Inherit		| +1			| +0			|
| | | | | 
| Object		| None	 		| +1			| +1		 	| 
| Object		| Single 		| +1			| +0		 	| 
| Object		| Collection 	| +1			| +0		 	| 
| Object		| Object		| +1			| +1			|
| Object		| Inherit		| +1			| +1			|

