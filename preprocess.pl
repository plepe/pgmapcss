#!/usr/bin/perl

%error_keys = ();

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

# now process test-template.mapnik and replace COLOR placeholders by colors
open $f, "<test-template.mapnik";
open $r, ">test.mapnik";
while (<$f>) {
  if (m/^# FOR (.*)$/) {
    @keys = split " ", $1;
    @t = ();
    while (<$f>) {
      if (m/^# END/) {
	last;
      }

      push @t, $_;
    }

    foreach $key (@keys) {
      @res = ();

      foreach $value (possible_values($key)) {
	if ($value eq '') {
	}
	elsif ($value eq '*') {
	  $error_keys{$key} = 1;
	}
	else {
	  foreach $row (@t) {
	    my $r1 = $row;
	    $r1 =~ s/\[$key\]/$value/;
	    push @res, $r1;
	  }
	}
      }

      @t = @res;
    }

    print $r join "", @t;
  }
  else {
    print $r $_;
  }
}
close($r);
close($f);

@error_keys = keys %error_keys;
if (@error_keys != 0) {
  print "WARNING! Some values for the following keys are calculated by an eval-statement. As pgmapcss can't guess the result of those statements some symbols might not get rendered.\n* ";
  print join("\n* ", @error_keys);
  print "\n";
}
