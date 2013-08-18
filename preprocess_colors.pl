#!/usr/bin/perl

# possible_values: return list of all possible values for a key
sub possible_values {
  my $key = $_[0];
# TODO: escape characters
  my @ret = ();

  my $v;
  my $r;
# TODO: user/pass/host parameters for psql
  open $v, "psql -t -A -c \"select value from (select key, unnest(cast(value as text[])) as value from each((test_stat()).properties_values)) t where key='$key';\"|";
  while($r = <$v>) {
    chop($r);
    push @ret, $r;
  }

  return @ret;
}

@colors = possible_values("color");

# now process test-template.mapnik and replace COLOR placeholders by colors
open $f, "<test-template.mapnik";
open $r, ">test.mapnik";
while (<$f>) {
  if (m/^# FOR COLORS (.*)$/) {
    $repl_var = $1;
    $t = "";
    while (<$f>) {
      if (m/^# END/) {
	last;
      }

      $t .= $_;
    }

    foreach (@colors) {
      my $u = $t;
      $u =~ s/$repl_var/$_/g;
      print $r $u;
    }

  }
  else {
    print $r $_;
  }
}
close($r);
close($f);
