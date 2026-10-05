#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <array>
#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <iomanip>

using namespace std;
namespace fs = std::filesystem;


// ============================================================
// CONFIG
// ============================================================

constexpr size_t CHARSET_SIZE = 92;
constexpr unsigned int CHARSET_START = 35; // '#'
constexpr size_t TOP_COUNT = 92;

constexpr size_t SPLIT_LIMIT = 1024 * 1024; // 1 MB
constexpr size_t BUFFER_SIZE = 1024 * 1024; // 1 MB


// ============================================================
// DATA STRUCTURES
// ============================================================

struct FrequencyEntry
{
    uint8_t byte;
    uint64_t frequency;
};


// ============================================================
// CHARSET
// ASCII 35 (#) through 126 (~)
// ============================================================

string getCharset()
{
    string charset;

    charset.reserve(CHARSET_SIZE);

    for (unsigned int i = 0; i < CHARSET_SIZE; ++i)
    {
        charset += static_cast<char>(
            CHARSET_START + i
        );
    }

    return charset;
}


// ============================================================
// COUNT BYTE FREQUENCIES
// ============================================================

bool countFrequencies(
    const string& fileName,
    array<uint64_t, 256>& frequencies
)
{
    frequencies.fill(0);

    ifstream input(
        fileName,
        ios::binary
    );

    if (!input)
    {
        cout << "Error opening input file.\n";
        return false;
    }

    vector<char> buffer(BUFFER_SIZE);

    while (input)
    {
        input.read(
            buffer.data(),
            buffer.size()
        );

        const streamsize bytesRead =
            input.gcount();

        for (streamsize i = 0; i < bytesRead; ++i)
        {
            const uint8_t byte =
                static_cast<uint8_t>(
                    buffer[i]
                );

            ++frequencies[byte];
        }
    }

    return true;
}


// ============================================================
// SORT ALL 256 BY FREQUENCY
//
// Highest frequency first.
// If frequencies are equal, lower byte value comes first.
// This makes the mapping deterministic.
// ============================================================

vector<FrequencyEntry> createFrequencyTable(
    const array<uint64_t, 256>& frequencies
)
{
    vector<FrequencyEntry> table;

    table.reserve(256);

    for (int i = 0; i < 256; ++i)
    {
        table.push_back({
            static_cast<uint8_t>(i),
            frequencies[i]
        });
    }

    sort(
        table.begin(),
        table.end(),
        [](const FrequencyEntry& a,
           const FrequencyEntry& b)
        {
            if (a.frequency != b.frequency)
                return a.frequency > b.frequency;

            return a.byte < b.byte;
        }
    );

    return table;
}


// ============================================================
// WRITE FREQUENCY TABLE
//
// Format:
//
// Rank    Byte    Frequency
// 1       32      123456
// 2       101     98765
// ...
// 256     255     0
// ============================================================

bool writeFrequencyTable(
    const string& fileName,
    const vector<FrequencyEntry>& table
)
{
    ofstream output(
        fileName,
        ios::binary
    );

    if (!output)
    {
        cout << "Error creating frequency table.\n";
        return false;
    }

    output << "Rank\tByte\tFrequency\n";

    for (size_t i = 0; i < table.size(); ++i)
    {
        output
            << (i + 1)
            << '\t'
            << static_cast<int>(table[i].byte)
            << '\t'
            << table[i].frequency
            << '\n';
    }

    return true;
}


// ============================================================
// PRINT FREQUENCY TABLE
// ============================================================

void printFrequencyTable(
    const vector<FrequencyEntry>& table
)
{
    cout << "\n";
    cout << "============================================================\n";
    cout << "                    FREQUENCY TABLE\n";
    cout << "============================================================\n";

    cout
        << left
        << setw(8) << "Rank"
        << setw(8) << "Byte"
        << setw(15) << "Frequency"
        << "Character\n";

    cout << "------------------------------------------------------------\n";

    for (size_t i = 0; i < table.size(); ++i)
    {
        const uint8_t byte = table[i].byte;

        cout
            << left
            << setw(8) << (i + 1)
            << setw(8) << static_cast<int>(byte)
            << setw(15) << table[i].frequency;

        if (byte >= 32 && byte <= 126)
        {
            cout << "'" << static_cast<char>(byte) << "'";
        }
        else
        {
            cout << "non-printable";
        }

        cout << '\n';
    }

    cout << "============================================================\n";
}


// ============================================================
// CREATE ENCODING TABLE
//
// For each original byte:
//
// top 92:
//     byte -> charset character
//
// remaining 164:
//     byte -> marker + charset character
//
// q=1:
//     positions 0..91
//
// q=2:
//     positions 92..163
// ============================================================

struct EncodingEntry
{
    char first;
    char second;
    uint8_t length;
};


array<EncodingEntry, 256> createEncodingTable(
    const vector<FrequencyEntry>& table,
    const string& charset
)
{
    array<EncodingEntry, 256> encoding{};

    // --------------------------------------------------------
    // Top 92 bytes = one character
    // --------------------------------------------------------

    for (size_t i = 0; i < TOP_COUNT; ++i)
    {
        const uint8_t originalByte =
            table[i].byte;

        encoding[originalByte] = {
            charset[i],
            '\0',
            1
        };
    }

    // --------------------------------------------------------
    // Remaining 164 bytes = two characters
    // --------------------------------------------------------

    for (size_t i = TOP_COUNT;
         i < table.size();
         ++i)
    {
        const uint8_t originalByte =
            table[i].byte;

        const size_t position =
            i - TOP_COUNT;

        const uint8_t q =
            static_cast<uint8_t>(
                1 + position / CHARSET_SIZE
            );

        const uint8_t r =
            static_cast<uint8_t>(
                position % CHARSET_SIZE
            );

        encoding[originalByte] = {
            static_cast<char>('!' + q - 1),
            charset[r],
            2
        };
    }

    return encoding;
}


// ============================================================
// CREATE DECODING TABLE
//
// One-character values:
//
// charset[0] -> top-ranked byte
// charset[1] -> second-ranked byte
// ...
//
// Two-character values:
//
// ! + charset[x] -> remaining byte
// " + charset[x] -> remaining byte
// ============================================================

array<uint8_t, CHARSET_SIZE> createTopDecodeTable(
    const vector<FrequencyEntry>& table
)
{
    array<uint8_t, CHARSET_SIZE> decode{};

    for (size_t i = 0; i < TOP_COUNT; ++i)
    {
        decode[i] = table[i].byte;
    }

    return decode;
}


array<uint8_t, 164> createRemainingDecodeTable(
    const vector<FrequencyEntry>& table
)
{
    array<uint8_t, 164> decode{};

    for (size_t i = TOP_COUNT;
         i < table.size();
         ++i)
    {
        decode[i - TOP_COUNT] = table[i].byte;
    }

    return decode;
}


// ============================================================
// PROGRESS
// ============================================================

void showProgress(
    uint64_t current,
    uint64_t total,
    const string& operation
)
{
    if (total == 0)
        return;

    constexpr int BAR_WIDTH = 40;

    const double percent =
        static_cast<double>(current) /
        static_cast<double>(total) *
        100.0;

    const int filled =
        static_cast<int>(
            BAR_WIDTH * percent / 100.0
        );

    cout << '\r'
         << operation
         << ": [";

    for (int i = 0; i < BAR_WIDTH; ++i)
    {
        if (i < filled)
            cout << '#';
        else
            cout << '-';
    }

    cout
        << "] "
        << fixed
        << setprecision(1)
        << percent
        << "%";

    cout.flush();
}


// ============================================================
// ENCODE + SPLIT
// ============================================================

void encodeAndSplit()
{
    const string charset = getCharset();

    string inputFile;
    string frequencyFile;

    cout << "Enter input file name: ";
    getline(cin >> ws, inputFile);

    if (!fs::exists(inputFile))
    {
        cout << "Error: Input file does not exist.\n";
        return;
    }

    const uintmax_t fileSize =
        fs::file_size(inputFile);

    if (fileSize == 0)
    {
        cout << "Error: Input file is empty.\n";
        return;
    }

    cout << "Enter frequency table file name: ";
    getline(cin >> ws, frequencyFile);

    if (frequencyFile.empty())
    {
        cout << "Error: Invalid frequency table name.\n";
        return;
    }

    // --------------------------------------------------------
    // PASS 1: Count frequencies
    // --------------------------------------------------------

    cout << "\nCounting byte frequencies...\n";

    array<uint64_t, 256> frequencies{};

    if (!countFrequencies(
            inputFile,
            frequencies))
    {
        return;
    }

    // --------------------------------------------------------
    // Sort frequency table
    // --------------------------------------------------------

    vector<FrequencyEntry> table =
        createFrequencyTable(frequencies);

    // --------------------------------------------------------
    // Save frequency table
    // --------------------------------------------------------

    if (!writeFrequencyTable(
            frequencyFile,
            table))
    {
        return;
    }

    // --------------------------------------------------------
    // Build encoding lookup table
    // --------------------------------------------------------

    const auto encoding =
        createEncodingTable(
            table,
            charset
        );

    // --------------------------------------------------------
    // PASS 2: Encode
    // --------------------------------------------------------

    ifstream input(
        inputFile,
        ios::binary
    );

    if (!input)
    {
        cout << "Error opening input file.\n";
        return;
    }

    vector<char> inputBuffer(BUFFER_SIZE);
    vector<char> outputBuffer(SPLIT_LIMIT);

    size_t outputSize = 0;

    int fileIndex = 1;

    ofstream output;

    auto openOutputFile = [&]() -> bool
    {
        if (output.is_open())
            output.close();

        const string name =
            to_string(fileIndex) + ".txt";

        output.open(
            name,
            ios::binary
        );

        if (!output)
        {
            cout
                << "\nError creating "
                << name
                << '\n';

            return false;
        }

        outputSize = 0;

        return true;
    };

    auto flushOutput = [&]()
    {
        if (outputSize > 0)
        {
            output.write(
                outputBuffer.data(),
                outputSize
            );

            outputSize = 0;
        }
    };

    if (!openOutputFile())
        return;

    uint64_t processed = 0;

    cout << "\nEncoding...\n";

    while (input)
    {
        input.read(
            inputBuffer.data(),
            inputBuffer.size()
        );

        const streamsize bytesRead =
            input.gcount();

        if (bytesRead <= 0)
            break;

        for (streamsize i = 0;
             i < bytesRead;
             ++i)
        {
            const uint8_t byte =
                static_cast<uint8_t>(
                    inputBuffer[i]
                );

            const EncodingEntry& encoded =
                encoding[byte];

            // ------------------------------------------------
            // Keep an encoded pair together.
            // ------------------------------------------------

            if (outputSize + encoded.length >
                SPLIT_LIMIT)
            {
                flushOutput();

                output.close();

                ++fileIndex;

                if (!openOutputFile())
                    return;
            }

            outputBuffer[outputSize++] =
                encoded.first;

            if (encoded.length == 2)
            {
                outputBuffer[outputSize++] =
                    encoded.second;
            }

            ++processed;
        }

        showProgress(
            processed,
            fileSize,
            "Encoding"
        );
    }

    flushOutput();

    output.close();
    input.close();

    cout << '\n';

    // --------------------------------------------------------
    // Print frequency table
    // --------------------------------------------------------

    printFrequencyTable(table);

    cout << "\nEncoding complete.\n";
    cout << "Input file: "
         << inputFile
         << '\n';

    cout << "Frequency table: "
         << frequencyFile
         << '\n';

    cout << "Text files created: "
         << fileIndex
         << '\n';
}


// ============================================================
// READ FREQUENCY TABLE
//
// Reads the 256 lines:
//
// Rank Byte Frequency
//
// Frequency itself is not needed for decoding.
// The sorted byte order is what defines the mapping.
// ============================================================

bool readFrequencyTable(
    const string& fileName,
    vector<FrequencyEntry>& table
)
{
    ifstream input(
        fileName
    );

    if (!input)
    {
        cout
            << "Error opening frequency table.\n";

        return false;
    }

    table.clear();
    table.reserve(256);

    string header;

    // Skip header
    getline(input, header);

    int rank;
    int byteValue;
    uint64_t frequency;

    while (
        input
        >> rank
        >> byteValue
        >> frequency
    )
    {
        if (byteValue < 0 ||
            byteValue > 255)
        {
            cout
                << "Error: Invalid byte value in "
                << "frequency table.\n";

            return false;
        }

        table.push_back({
            static_cast<uint8_t>(byteValue),
            frequency
        });
    }

    if (table.size() != 256)
    {
        cout
            << "Error: Frequency table must contain "
            << "exactly 256 byte values.\n";

        return false;
    }

    // Make sure every byte 0..255 occurs exactly once.
    array<bool, 256> found{};

    for (const auto& entry : table)
    {
        if (found[entry.byte])
        {
            cout
                << "Error: Duplicate byte in "
                << "frequency table.\n";

            return false;
        }

        found[entry.byte] = true;
    }

    return true;
}


// ============================================================
// DECODE + MERGE
// ============================================================

void decodeAndMerge()
{
    const string charset = getCharset();

    string outputFile;
    string frequencyFile;

    cout << "Enter output file name: ";
    getline(cin >> ws, outputFile);

    cout << "Enter frequency table file: ";
    getline(cin >> ws, frequencyFile);

    // --------------------------------------------------------
    // Read frequency table
    // --------------------------------------------------------

    vector<FrequencyEntry> table;

    if (!readFrequencyTable(
            frequencyFile,
            table))
    {
        return;
    }

    const auto topDecode =
        createTopDecodeTable(table);

    const auto remainingDecode =
        createRemainingDecodeTable(table);

    // --------------------------------------------------------
    // Number of encoded files
    // --------------------------------------------------------

    int numFiles;

    cout << "Enter number of text files: ";
    cin >> numFiles;

    if (numFiles <= 0)
    {
        cout
            << "Error: Invalid number of files.\n";

        return;
    }

    // --------------------------------------------------------
    // Calculate total encoded size
    // --------------------------------------------------------

    uintmax_t totalSize = 0;

    for (int i = 1; i <= numFiles; ++i)
    {
        const string fileName =
            to_string(i) + ".txt";

        if (!fs::exists(fileName))
        {
            cout
                << "Error: Missing file "
                << fileName
                << '\n';

            return;
        }

        totalSize += fs::file_size(fileName);
    }

    // --------------------------------------------------------
    // Open output
    // --------------------------------------------------------

    ofstream output(
        outputFile,
        ios::binary
    );

    if (!output)
    {
        cout
            << "Error creating output file.\n";

        return;
    }

    vector<char> inputBuffer(BUFFER_SIZE);
    vector<char> outputBuffer(BUFFER_SIZE);

    size_t outputSize = 0;

    auto flushOutput = [&]()
    {
        if (outputSize > 0)
        {
            output.write(
                outputBuffer.data(),
                outputSize
            );

            outputSize = 0;
        }
    };

    // --------------------------------------------------------
    // Marker state
    //
    // A marker can theoretically be the final character
    // of one input buffer/file and its data character can
    // be the first character of the next one.
    // --------------------------------------------------------

    bool pendingMarker = false;
    uint8_t pendingQ = 0;

    uint64_t processed = 0;

    // --------------------------------------------------------
    // Decode every text file
    // --------------------------------------------------------

    for (int fileIndex = 1;
         fileIndex <= numFiles;
         ++fileIndex)
    {
        const string fileName =
            to_string(fileIndex) + ".txt";

        ifstream input(
            fileName,
            ios::binary
        );

        if (!input)
        {
            cout
                << "\nError opening "
                << fileName
                << '\n';

            return;
        }

        while (input)
        {
            input.read(
                inputBuffer.data(),
                inputBuffer.size()
            );

            const streamsize bytesRead =
                input.gcount();

            if (bytesRead <= 0)
                break;

            size_t position = 0;

            while (
                position <
                static_cast<size_t>(bytesRead)
            )
            {
                const uint8_t code =
                    static_cast<uint8_t>(
                        inputBuffer[position++]
                    );

                // ------------------------------------------------
                // If a marker is waiting, this character is
                // its r value.
                // ------------------------------------------------

                if (pendingMarker)
                {
                    if (
                        code < CHARSET_START ||
                        code >=
                            CHARSET_START +
                            CHARSET_SIZE
                    )
                    {
                        cout
                            << "\nError: Invalid encoded "
                            << "character after marker.\n";

                        return;
                    }

                    const uint8_t r =
                        static_cast<uint8_t>(
                            code - CHARSET_START
                        );

                    const size_t index =
                        (pendingQ - 1) *
                        CHARSET_SIZE +
                        r;

                    if (index >= 164)
                    {
                        cout
                            << "\nError: Invalid two-character "
                            << "sequence.\n";

                        return;
                    }

                    const uint8_t original =
                        remainingDecode[index];

                    outputBuffer[outputSize++] =
                        static_cast<char>(original);

                    pendingMarker = false;

                    if (outputSize ==
                        BUFFER_SIZE)
                    {
                        flushOutput();
                    }

                    continue;
                }

                // ------------------------------------------------
                // Marker
                // ! = q=1
                // " = q=2
                // ------------------------------------------------

                if (code == '!' ||
                    code == '"')
                {
                    pendingQ =
                        static_cast<uint8_t>(
                            code - '!' + 1
                        );

                    pendingMarker = true;

                    continue;
                }

                // ------------------------------------------------
                // One-character value
                // ------------------------------------------------

                if (
                    code < CHARSET_START ||
                    code >=
                        CHARSET_START +
                        CHARSET_SIZE
                )
                {
                    cout
                        << "\nError: Invalid encoded "
                        << "character.\n";

                    return;
                }

                const uint8_t r =
                    static_cast<uint8_t>(
                        code - CHARSET_START
                    );

                const uint8_t original =
                    topDecode[r];

                outputBuffer[outputSize++] =
                    static_cast<char>(original);

                if (outputSize ==
                    BUFFER_SIZE)
                {
                    flushOutput();
                }
            }

            processed +=
                static_cast<uint64_t>(
                    bytesRead
                );

            showProgress(
                processed,
                totalSize,
                "Decoding"
            );
        }

        input.close();
    }

    // --------------------------------------------------------
    // Marker without a following character
    // means corrupted/incomplete data.
    // --------------------------------------------------------

    if (pendingMarker)
    {
        cout
            << "\nError: Encoded data ends with "
            << "an incomplete marker.\n";

        return;
    }

    flushOutput();

    output.close();

    cout << '\n';

    cout
        << "Decoding complete.\n";

    cout
        << "Saved as: "
        << outputFile
        << '\n';
}


// ============================================================
// MAIN
// ============================================================

int main()
{
    cout
        << "============================================\n"
        << "      FREQUENCY BASED FILE ENCODER\n"
        << "============================================\n\n";

    cout
        << "1. Normal file bytes into text files\n"
        << "2. Text files into normal file bytes\n\n";

    cout << "Enter your choice: ";

    int choice;
    cin >> choice;

    switch (choice)
    {
        case 1:
            encodeAndSplit();
            break;

        case 2:
            decodeAndMerge();
            break;

        default:
            cout
                << "Invalid choice!\n";
            break;
    }

    return 0;
}
