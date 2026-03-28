#include <iostream>
#include <fstream>
using namespace std;
int main()
{
    char code[2];
    unsigned char ch;
    fstream input, output;
    string fileName;
    cout << "Enter file name for output: ";
    getline(cin >> ws, fileName);
    int i, num;
    cout << "Enter number of text files: ";
    cin >> num;
    output.open(fileName, ios::out | ios::binary);
    for (i = 1; i <= num; i++)
    {
        input.open(to_string(i) + ".txt", ios::in | ios::binary);
        input.seekg(0, ios::end);
        long long int j, limit = input.tellg();
        input.seekg(0, ios::beg);
        for (j = 0; j < limit; j += 2)
        {
            input.read((char *)code, 2 * sizeof(char));
            ch = 26 * (code[0] - 97) + (code[1] - 97);
            output.write((char *)&ch, sizeof(ch));
        }
        input.close();
    }
    output.close();
}
