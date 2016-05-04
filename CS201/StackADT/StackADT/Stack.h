/* Coded by Muratcan �i�ek S004233 Computer Science */

#include "StackItem.h"
class Stack
{
public:
	Stack();
	Stack(int size);
	~Stack();
	StackItem* pop();
	StackItem* top();
	void push(StackItem* item);
	bool isEmpty();
private:
	StackItem *head;
};

