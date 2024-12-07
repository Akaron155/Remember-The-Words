package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"os"
	"strings"
	"time"
)

// Color definitions
const (
	Reset  = "\033[0m"
	Red    = "\033[31m"
	Green  = "\033[32m"
	Yellow = "\033[33m"
	Cyan   = "\033[36m"
)

// Global configurations
var tempFolderPath = "./tempfile"

func init() {
	rand.Seed(time.Now().UnixNano())
}

// ReadWordsFromTxt reads words from a text file and returns them as a slice of strings.
func ReadWordsFromTxt(filePath string) ([]string, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var words []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		words = append(words, strings.TrimSpace(scanner.Text()))
	}
	return words, scanner.Err()
}

// GetPhonetic retrieves the phonetics of a word from Youdao Dictionary API.
func GetPhonetic(word string, phoneticType int) (string, error) {
	url := fmt.Sprintf("https://dict.youdao.com/result?word=%s&lang=en", word)
	resp, err := http.Get(url)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	// Parsing the response is omitted for brevity. Use a library like goquery for HTML parsing.
	return fmt.Sprintf("Phonetics for '%s' retrieved (dummy implementation)", word), nil
}

// SearchWordInDictYoudao queries the Youdao Dictionary for word details.
func SearchWordInDictYoudao(word string) (string, error) {
	url := fmt.Sprintf("http://dict.youdao.com/suggest?num=10000&ver=3.0&doctype=json&cache=false&le=en&q=%s", word)
	resp, err := http.Get(url)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	var result map[string]interface{}
	err = json.Unmarshal(body, &result)
	if err != nil {
		return "", err
	}

	// Simplified parsing
	data, _ := json.MarshalIndent(result, "", "  ")
	return string(data), nil
}

// Pause pauses the program until the user presses Enter.
func Pause(message string) {
	fmt.Println(message)
	bufio.NewReader(os.Stdin).ReadBytes('\n')
}

func main() {
	// Example usage
	filePath := "./words.txt"
	words, err := ReadWordsFromTxt(filePath)
	if err != nil {
		fmt.Println(Red, "Error reading words:", err, Reset)
		return
	}

	fmt.Println(Green, "Words loaded successfully!", Reset)
	for len(words) > 0 {
		word := words[0]
		words = words[1:]
		fmt.Printf(Cyan+"Processing word: %s"+Reset+"\n", word)

		phonetic, err := GetPhonetic(word, 0)
		if err != nil {
			fmt.Println(Red, "Error fetching phonetic:", err, Reset)
			continue
		}
		fmt.Println(Green, phonetic, Reset)

		Pause("Press Enter to proceed to the next word...")
	}

	fmt.Println(Green, "All words processed successfully!", Reset)
}
