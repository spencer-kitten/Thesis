#!/usr/bin/env ruby -w

require 'colorize'

String.disable_colorization false

require 'optparse'
require 'datafarming/error_handling'
require 'datafarming/cross'

help_msg = [
  'Create a crossed design from two or more input design files',
  'where each line is a design point.  The crossed design is',
  'written to ' + 'stdout'.blue + ' in CSV format.', '',
  'Syntax:',
  "\n\t#{ErrorHandling.prog_name} [--help] filenames...".yellow, '',
  "Arguments in square brackets are optional.  A vertical bar '|'",
  'indicates valid alternatives for invoking the option.  Prefix',
  'the command with "' + 'ruby'.yellow +
    '" if it is not on your PATH.', '',
  '  --help | -h | -? | ?'.green,
  "\tProduce this help message.",
  '  filenames...'.green,
  "\tThe names of the files containing designs to be crossed.",
  "\tInput file data can be delimited by commas, semicolons,",
  "\tcolons, or whitespace."
]

OptionParser.new do |opts|
  opts.banner = "Usage: #{$PROGRAM_NAME} [-h|--help] [filenames...[]"
  opts.on('-h', '-?', '--help') { ErrorHandling.clean_abort help_msg }
end.parse!

ErrorHandling.clean_abort help_msg if ARGV[0] == '?' || ARGV.length < 2

input_array = []
ARGV.each do |filename| # for each file given as a command-line arg...
  # open the file, read all the lines, and then for each line use
  # spaces, commas, colons, or semicolons to tokenize.
  input_array << File.open(filename).readlines.map do |line|
    line.strip.split(/[,:;]|\s+/)
  end
end
CrossedDesigns.cross(input_array).each { |line| puts line.join(',') }
