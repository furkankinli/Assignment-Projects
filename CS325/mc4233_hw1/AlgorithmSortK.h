/* Coded by Muratcan �i�ek S004233 Computer Science */
#ifndef  ALGORITHMSORTK_H
#define  ALGORITHMSORTK_H
#include "SelectionAlgorithm.h"

class AlgorithmSortK :
	public SelectionAlgorithm
{
public:
	AlgorithmSortK(int k);
	int select();
	~AlgorithmSortK();
};

#endif 
