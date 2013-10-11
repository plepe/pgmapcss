#!/usr/bin/perl

sub parse_file {
  my $FILE = $_[0];
  my $ret = "";

  open $f, "<$FILE";

  $open_comment = 0;

  while (<$f>) {
    chop;
    $next_open_comment = $open_comment;

    while ($_) {
      # print "$open_comment $_\n";

      if ($open_comment == 0) {
	if (m/(.*)\/\//) {
	  $_ = $1;
	}
	elsif (m/(.*)\/\*(.*)\*\/(.*)/) {
	  $_ = "$1$3";
	}
	elsif (m/(.*)\/\*/) {
	  $_ = $1;
	  $next_open_comment = 1;
	}
	elsif (m/(.*)\@import([^;]*);($3)/) {
	  $_ = "$1$3";

	  # TODO: import file!
	}
	else {
	  $ret .= "$_\n";
	  $_ = '';
	}
      }
      else {
	if (m/\*\/(.*)$/) {
	  $_ = $1;
	  $open_comment = 0;
	  $next_open_comment = 0;
	}
	else {
	  $_ = '';
	}
      }
    }

    $open_comment = $next_open_comment;
  }

  return $ret;
}

my $FILE=$ARGV[0];

print parse_file($FILE);
