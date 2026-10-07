#include <iostream>

struct Node {
    int data;
    Node* next;
    Node(int val) : data(val), next(nullptr) {}
};

// Insert a new node at the front of the list
void push(Node** head_ref, int new_data) {
    Node* new_node = new Node(new_data);
    new_node->next = *head_ref;
    *head_ref = new_node;
}

// Reverse the linked list iteratively
Node* reverseList(Node* head) {
    Node* prev = nullptr;
    Node* current = head;
    Node* next = nullptr;
    while (current != nullptr) {
        next = current->next;   // store next
        current->next = prev;   // reverse current's pointer
        prev = current;         // move prev forward
        current = next;         // move current forward
    }
    return prev; // new head
}

// Print the linked list
void printList(Node* node) {
    while (node != nullptr) {
        std::cout << node->data << " ";
        node = node->next;
    }
    std::cout << std::endl;
}

int main() {
    Node* head = nullptr;
    // Create list 1->2->3->4->5
    for (int i = 5; i >= 1; --i) {
        push(&head, i);
    }

    std::cout << "Original list: ";
    printList(head);

    head = reverseList(head);

    std::cout << "Reversed list: ";
    printList(head);
    return 0;
}
