#!/usr/bin/env ruby -w

require 'rubygems' if RUBY_VERSION =~ /^1\.8/
require 'colorize'

String.disable_colorization false

require 'optparse'
require 'datafarming/error_handling'

begin
  require 'quickstats'
rescue LoadError
  ErrorHandling.clean_abort [
    "\n\tALERT: quickstats gem is not installed!".red,
    "\tIf you have network connectivity, type:",
    "\n\t\tgem install quickstats\n".yellow,
    "\t(Admin privileges may be required.)\n\n"
  ]
end

help_msg = [
  'Calculate MSER truncation statistics for one or more input files.', '',
  'Input files should consist of one column of data per file, with or',
  'without headers.  The output consists of one line per input file,',
  'comprised of the MSER-based average of the data, the number of',
  'observations used to calculate that average, and the number of',
  'observations truncated, separated by commas.  Output is written',
  'to ' + 'stdout'.blue + ' in CSV format, with headers.', '',
  'Syntax:',
  "\n\t#{ErrorHandling.prog_name} [--help] filenames...".yellow, '',
  "Arguments in square brackets are optional.  A vertical bar '|'",
  'indicates valid alternatives for invoking the option.  Prefix',
  'the command with "' + 'ruby'.yellow +
  '" if it is not on your PATH.', '',
  '  --help | -h | -? | ?'.green,
  "\tProduce this help message.",
  '  filenames...'.green,
  "\tThe names of two or more files containing data to be analyzed."
]

OptionParser.new do |opts|
  opts.banner = "Usage: #{$PROGRAM_NAME} [-h|--help] filenames..."
  opts.on('-h', '-?', '--help') { ErrorHandling.clean_abort help_msg }
end.parse!

ErrorHandling.clean_abort help_msg if ARGV.empty? || ARGV[0] == '?'

puts 'x-bar,n,trunc'

ARGV.each do |fname|
  data = File.readlines(fname)
  data.shift if data[0] =~ /[A-Za-z]/ # strip header if one present
  data.map! { |line| line.chomp.strip.to_f }
  m_stats = QuickStats.new
  warmup = [(data.length * 0.5).to_i, data.length - 10].min
  index = data.length - 1
  while index > (data.length - warmup) && index > 1
    m_stats.new_obs(data[index])
    index -= 1
  end
  best = [m_stats.std_err, m_stats.avg, warmup]

  while index > -1
    m_stats.new_obs(data[index])
    best = [m_stats.std_err, m_stats.avg, index] if m_stats.std_err <= best[0]
    index -= 1
  end

  printf "%f,%d,%d\n", best[1], data.length - best[2], best[2]
end
