/* Coded by Muratcan �i�ek S004233 Computer Science */
#ifndef ALGORITHMSORTALL_H
#define ALGORITHMSORTALL_H
#include "SelectionAlgorithm.h"

class AlgorithmSortAll :
	public SelectionAlgorithm
{
public:
	AlgorithmSortAll(int k);
	int select();
	~AlgorithmSortAll();
};

#endif 
