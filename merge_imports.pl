#!/usr/bin/perl

sub import_file {
  my $url_desc = $_[0];
  my $file;

  if ($url_desc =~ /url\("(.*)"\)/) {
    $file = $1;
  }
  elsif ($url_desc =~ /url\('(.*)'\)/) {
    $file = $1;
  }
  elsif ($url_desc =~ /url\((.*)\)/) {
    $file = $1;
  }
  elsif ($url_desc =~ /\s*(.*)\s*/) {
    $file = $1;
  }

  my $f;
  open $f, "<$file";

  my @ret = <$f>;

  close($f);

  return @ret;
}

sub parse_file {
  my $FILE = $_[0];
  my $ret = "";

  open $f, "<$FILE";
  @lines = <$f>;

  $open_comment = 0;

  while (scalar @lines) {
    $_ = shift @lines;
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
	  $_ = $1;

	  @lines = ( import_file($2), $3, @lines );
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
